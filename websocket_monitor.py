import threading
import time
import logging
import websocket
import json

class WebSocketMonitor:
    def __init__(self):
        self.connection_status = {"connected": False, "last_ping": 0}
        self.reconnect_attempts = 0
        self.max_reconnects = 10
        
    def monitor_connection(self, ws_url, on_message_callback):
        def on_message(ws, message):
            self.connection_status["last_ping"] = time.time()
            on_message_callback(ws, message)
            
        def on_error(ws, error):
            logging.error(f"WebSocket error: {error}")
            self.connection_status["connected"] = False
            
        def on_close(ws, close_status_code, close_msg):
            self.connection_status["connected"] = False
            if self.reconnect_attempts < self.max_reconnects:
                self.reconnect_attempts += 1
                time.sleep(min(self.reconnect_attempts * 2, 30))
                self.start_connection(ws_url, on_message_callback)
                
        def on_open(ws):
            self.connection_status["connected"] = True
            self.reconnect_attempts = 0
            
        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, 
                                   on_close=on_close, on_open=on_open)
        ws.run_forever()
        
    def start_connection(self, ws_url, on_message_callback):
        threading.Thread(target=self.monitor_connection, args=(ws_url, on_message_callback), daemon=True).start()
        
    def is_healthy(self):
        return self.connection_status["connected"] and (time.time() - self.connection_status["last_ping"]) < 60

monitor = WebSocketMonitor()
