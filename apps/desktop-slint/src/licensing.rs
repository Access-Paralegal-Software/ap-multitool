use std::fs;
use std::path::PathBuf;

use chrono::{NaiveDate, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

const LOCAL_PEPPER: &str = "APM_OFFLINE_SECRET_SALT_2026";
const SIGNING_SECRET: &[u8] = b"AP_MULTITOOL_OFFLINE_SECRET_2026_PROD";
const FOUNDER_PASS_URL: &str = "https://buy.stripe.com/eVqfZj0mc0Owb0Ch178Vi00";

#[derive(Serialize, Deserialize, Debug)]
pub struct LicenseCache {
    pub key: String,
    pub cached_at: String,
    pub signature: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OfflineKeyClaims {
    pub seat: String,
    pub key_type: String,
    pub expires_on: NaiveDate,
}

#[derive(Deserialize)]
struct KeyPayload {
    v: u32,
    #[serde(rename = "type")]
    key_type: String,
    seat: String,
    exp: String,
}

pub struct LicenseManager {
    cache_path: PathBuf,
}

impl LicenseManager {
    pub fn new() -> Self {
        let home = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
        Self::with_cache(home.join(".access_paralegal_entitlement.json"))
    }

    pub fn with_cache(cache_path: PathBuf) -> Self {
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
            return (false, "14-day evaluation active".to_string());
        }

        let content = match fs::read_to_string(&self.cache_path) {
            Ok(c) => c,
            Err(_) => return (false, "Evaluation mode".to_string()),
        };

        let cache: LicenseCache = match serde_json::from_str(&content) {
            Ok(c) => c,
            Err(_) => return (false, "Evaluation mode".to_string()),
        };

        let expected_sig = Self::compute_signature(&cache.key, &cache.cached_at);
        if expected_sig != cache.signature {
            return (false, "Invalid license signature".to_string());
        }

        match validate_offline_key(&cache.key) {
            Ok(claims) => (true, badge_for(&claims)),
            Err(err) => (false, err),
        }
    }

    pub fn activate_offline_key(&self, key: &str) -> Result<String, String> {
        let claims = validate_offline_key(key)?;
        let stored_key = normalize_key_text(key);
        let now = Utc::now().to_rfc3339();
        let sig = Self::compute_signature(&stored_key, &now);

        let cache = LicenseCache {
            key: stored_key,
            cached_at: now,
            signature: sig,
        };

        let json = serde_json::to_string_pretty(&cache).map_err(|e| e.to_string())?;
        fs::write(&self.cache_path, json).map_err(|e| format!("Could not save the license file: {e}"))?;
        Ok(badge_for(&claims))
    }

    pub fn open_store() {
        let _ = webbrowser::open(FOUNDER_PASS_URL);
    }
}

pub fn validate_offline_key(key: &str) -> Result<OfflineKeyClaims, String> {
    let compact = normalize_key_text(key);
    if compact.len() < 16 {
        return Err("Offline license key is not valid".to_string());
    }

    let decoded = decode_base32(&compact).map_err(|_| "Offline license key is not valid".to_string())?;
    let dot = decoded
        .iter()
        .position(|byte| *byte == b'.')
        .ok_or_else(|| "Offline license key is not valid".to_string())?;
    let payload = &decoded[..dot];
    let sig = &decoded[dot + 1..];
    if sig.len() != 8 {
        return Err("Offline license key is not valid".to_string());
    }

    let full = hmac_sha256(SIGNING_SECRET, payload);
    if !constant_eq(&full[..8], sig) {
        return Err("Offline license key is not valid".to_string());
    }

    let parsed: KeyPayload = serde_json::from_slice(payload)
        .map_err(|_| "Offline license key is not valid".to_string())?;
    if parsed.v != 1 {
        return Err("Offline license key is not valid".to_string());
    }
    if !matches!(parsed.key_type.as_str(), "trial" | "founder" | "commercial") {
        return Err("Offline license key is not valid".to_string());
    }
    if parsed.seat.is_empty() || parsed.seat.len() > 64 || !seat_chars_ok(&parsed.seat) {
        return Err("Offline license key is not valid".to_string());
    }

    let expires_on = NaiveDate::parse_from_str(&parsed.exp, "%Y-%m-%d")
        .map_err(|_| "Offline license key is not valid".to_string())?;
    if Utc::now().date_naive() > expires_on {
        return Err("Offline license key expired".to_string());
    }

    Ok(OfflineKeyClaims {
        seat: parsed.seat,
        key_type: parsed.key_type,
        expires_on,
    })
}

fn badge_for(claims: &OfflineKeyClaims) -> String {
    match claims.key_type.as_str() {
        "trial" => "Evaluation key active".to_string(),
        "founder" => "Founder license active".to_string(),
        _ => "Offline license active".to_string(),
    }
}

fn normalize_key_text(key: &str) -> String {
    key.chars()
        .filter(|ch| !ch.is_whitespace() && *ch != '-')
        .map(|ch| ch.to_ascii_uppercase())
        .collect()
}

fn seat_chars_ok(seat: &str) -> bool {
    seat.chars()
        .all(|ch| ch.is_ascii_alphanumeric() || ch == '_' || ch == '-')
}

fn constant_eq(left: &[u8], right: &[u8]) -> bool {
    if left.len() != right.len() {
        return false;
    }
    let mut diff = 0u8;
    for (a, b) in left.iter().zip(right.iter()) {
        diff |= a ^ b;
    }
    diff == 0
}

fn hmac_sha256(key: &[u8], message: &[u8]) -> [u8; 32] {
    const BLOCK: usize = 64;
    let mut keyed = [0u8; BLOCK];
    if key.len() > BLOCK {
        let mut hasher = Sha256::new();
        hasher.update(key);
        keyed[..32].copy_from_slice(&hasher.finalize());
    } else {
        keyed[..key.len()].copy_from_slice(key);
    }

    let mut ipad = [0u8; BLOCK];
    let mut opad = [0u8; BLOCK];
    for i in 0..BLOCK {
        ipad[i] = keyed[i] ^ 0x36;
        opad[i] = keyed[i] ^ 0x5c;
    }

    let mut inner = Sha256::new();
    inner.update(ipad);
    inner.update(message);
    let inner_hash = inner.finalize();

    let mut outer = Sha256::new();
    outer.update(opad);
    outer.update(inner_hash);
    let outer_hash = outer.finalize();

    let mut out = [0u8; 32];
    out.copy_from_slice(&outer_hash);
    out
}

fn decode_base32(input: &str) -> Result<Vec<u8>, ()> {
    let mut padded = input.to_string();
    while padded.len() % 8 != 0 {
        padded.push('=');
    }

    let mut buffer: u64 = 0;
    let mut bits: u32 = 0;
    let mut out = Vec::new();
    for ch in padded.chars() {
        if ch == '=' {
            break;
        }
        let value = base32_value(ch).ok_or(())?;
        buffer = (buffer << 5) | u64::from(value);
        bits += 5;
        if bits >= 8 {
            bits -= 8;
            out.push(((buffer >> bits) & 0xff) as u8);
        }
    }
    Ok(out)
}

fn base32_value(ch: char) -> Option<u8> {
    match ch {
        'A'..='Z' => Some((ch as u8) - b'A'),
        '2'..='7' => Some((ch as u8) - b'2' + 26),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const VALID_KEY: &str = "PMRGK-6DQEI-5CEMR-QGI3S-2MJRF-UYDCI-RMEJU-WC5BC-HIRDE-MBSGY-WTCMJ-NGAYS-ELBCO-NSWC5-BCHIR-ECTCQ-JBAS2-MBREI-WCE5D-ZOBSS-EORCO-RZGSY-LMEIW-CE5RC-HIYX2-LV6UN-6GBQY-UEAOQ";
    const EXPIRED_KEY: &str = "PMRGK-6DQEI-5CEMR-QGIYC-2MBRF-UYDCI-RMEJU-WC5BC-HIRDE-MBSGY-WTCMJ-NGAYS-ELBCO-NSWC5-BCHIR-ECTCQ-JBAS2-MBREI-WCE5D-ZOBSS-EORCO-RZGSY-LMEIW-CE5RC-HIYX2-LUFNL-KQ6OE-7WBTQ";

    #[test]
    fn accepts_signed_unexpired_eval_key() {
        let claims = validate_offline_key(VALID_KEY).expect("valid key");
        assert_eq!(claims.seat, "ALPHA-01");
        assert_eq!(claims.key_type, "trial");
        assert_eq!(claims.expires_on, NaiveDate::from_ymd_opt(2027, 11, 1).unwrap());
    }

    #[test]
    fn rejects_expired_and_tampered_keys() {
        let err = validate_offline_key(EXPIRED_KEY).unwrap_err();
        assert_eq!(err, "Offline license key expired");

        let mut tampered = VALID_KEY.to_string();
        tampered.replace_range(0..1, "A");
        assert_eq!(
            validate_offline_key(&tampered).unwrap_err(),
            "Offline license key is not valid"
        );
        assert_eq!(
            validate_offline_key("APM-2026-BATE-FOUNDER-PASS").unwrap_err(),
            "Offline license key is not valid"
        );
    }

    #[test]
    fn activation_cache_verifies_without_network() {
        let path = std::env::temp_dir().join(format!(
            "ap-license-test-{}-{}.json",
            std::process::id(),
            Utc::now().timestamp_millis()
        ));
        let mgr = LicenseManager::with_cache(path.clone());
        let badge = mgr.activate_offline_key(VALID_KEY).expect("activate");
        assert_eq!(badge, "Evaluation key active");
        let (active, text) = mgr.verify_offline();
        assert!(active);
        assert_eq!(text, "Evaluation key active");

        let mut cache: LicenseCache =
            serde_json::from_str(&fs::read_to_string(&path).unwrap()).unwrap();
        cache.signature = "00".repeat(32);
        fs::write(&path, serde_json::to_string(&cache).unwrap()).unwrap();
        let (active, text) = mgr.verify_offline();
        assert!(!active);
        assert_eq!(text, "Invalid license signature");
        let _ = fs::remove_file(path);
    }
}
