use std::time::Duration;
use reqwest::Response;
use {backoff::{ExponentialBackoff, backoff::Backoff}};
use {tokio_retry::strategy::{ExponentialBackoff as RetryBackoff, jitter}};
use tokio_retry::Retry;

pub struct RetryableClient {
    client: reqwest::Client,
}

impl RetryableClient {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::builder()
                .timeout(Duration::from_millis(2000))
                .build()
                .unwrap(),
        }
    }
    
    pub async fn post_with_retry(
        &self,
        url: &str,
        headers: std::collections::HashMap<String, String>,
        body: String,
    ) -> Result<Response, Box<dyn std::error::Error + Send + Sync>> {
        let retry_strategy = RetryBackoff::from_millis(100)
            .max_delay(Duration::from_secs(2))
            .take(3); // 3 retries total
        
        let operation = || async {
            let mut request = self.client.post(url);
            
            // Add headers
            for (key, value) in &headers {
                request = request.header(key, value);
            }
            
            let response = request
                .header("Content-Type", "application/json")
                .body(body.clone())
                .send()
                .await?;
            
            // Check if we should retry based on status
            if response.status().is_server_error() || response.status() == 429 {
                return Err(format!("Retryable error: {}", response.status()));
            }
            
            Ok(response)
        };
        
        match Retry::spawn(retry_strategy, operation).await {
            Ok(response) => Ok(response),
            Err(e) => Err(format!("All retries failed: {}", e).into()),
        }
    }
    
    pub async fn get_with_retry(
        &self,
        url: &str,
        headers: std::collections::HashMap<String, String>,
    ) -> Result<Response, Box<dyn std::error::Error + Send + Sync>> {
        let retry_strategy = RetryBackoff::from_millis(100)
            .max_delay(Duration::from_secs(2))
            .take(3);
        
        let operation = || async {
            let mut request = self.client.get(url);
            
            for (key, value) in &headers {
                request = request.header(key, value);
            }
            
            let response = request.send().await?;
            
            if response.status().is_server_error() || response.status() == 429 {
                return Err(format!("Retryable error: {}", response.status()));
            }
            
            Ok(response)
        };
        
        match Retry::spawn(retry_strategy, operation).await {
            Ok(response) => Ok(response),
            Err(e) => Err(format!("All retries failed: {}", e).into()),
        }
    }
}
