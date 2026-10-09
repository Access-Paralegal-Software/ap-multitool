use std::fs;
use std::path::PathBuf;
use sha2::{Sha256, Digest};
use chrono::{DateTime, Utc, Duration};
use serde::{Deserialize, Serialize};

const LOCAL_PEPPER: &str = "APM_OFFLINE_SECRET_SALT_2026";
const FOUNDER_PASS_URL: &str = "https://buy.stripe.com/eVqfZj0mc0Owb0Ch178Vi00";

#[derive(Serialize, Deserialize, Debug)]
pub struct LicenseCache {
    pub key: String,
    pub cached_at: String,
    pub signature: String,
}

pub struct LicenseManager {
    cache_path: PathBuf,
}

impl LicenseManager {
    pub fn new() -> Self {
        let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
        let cache_path = home.join(".access_paralegal_entitlement.json");
        Self { cache_path }
    }

    pub fn compute_signature(key: &str, cached_at: &str) -> String {
        let payload = format!("{}::{}::{}", key, cached_at, LOCAL_PEPPER);
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        format!("{:x}", hasher.finalize())
    }

    pub fn verify_offline(&self) -> (bool, String) {
        if !self.cache_path.exists() {
            return (false, "14-Day Evaluation Active".to_string());
        }

        let content = match fs::read_to_string(&self.cache_path) {
            Ok(c) => c,
            Err(_) => return (false, "Evaluation Mode".to_string()),
        };

        let cache: LicenseCache = match serde_json::from_str(&content) {
            Ok(c) => c,
            Err(_) => return (false, "Evaluation Mode".to_string()),
        };

        let expected_sig = Self::compute_signature(&cache.key, &cache.cached_at);
        if expected_sig != cache.signature {
            return (false, "Invalid License Signature".to_string());
        }

        // Validate 7-day offline verification freshness window
        if let Ok(cached_time) = DateTime::parse_from_rfc3339(&cache.cached_at) {
            let now = Utc::now();
            let expiry = cached_time + Duration::days(7);
            if now > expiry {
                return (false, "Offline Cache Expired (Reconnect or Re-enter Key)".to_string());
            }
        }

        (true, "Commercial Founder Pass Active".to_string())
    }

    #[allow(dead_code)]
pub fn activate_offline_key(&self, key: &str) -> Result<(), String> {
        let clean_key = key.trim().to_uppercase();
        if clean_key.len() < 16 {
            return Err("Invalid license key format".to_string());
        }

        let now = Utc::now().to_rfc3339();
        let sig = Self::compute_signature(&clean_key, &now);

        let cache = LicenseCache {
            key: clean_key,
            cached_at: now,
            signature: sig,
        };

        let json = serde_json::to_string_pretty(&cache).map_err(|e| e.to_string())?;
        fs::write(&self.cache_path, json).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn open_store() {
        let _ = webbrowser::open(FOUNDER_PASS_URL);
    }
}

