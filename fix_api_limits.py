import time
import requests
from functools import wraps

def rate_limit(delay=1.0):
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = delay - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(2.0)
def get_btc_dominance():
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=10,
            headers={'User-Agent': 'HFT-System/1.0'}
        )
        if response.status_code == 200:
            data = response.json()
            return float(data['data']['market_cap_percentage']['btc'])
    except:
        pass
    return 45.0
