import json
import os

config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, "r") as f:
    config = json.load(f)

# 1. Ensure provider structural skeleton
if "models" not in config:
    config["models"] = {}
if "providers" not in config["models"]:
    config["models"]["providers"] = {}

# 2. Build the Anthropic Provider entry
config["models"]["providers"]["anthropic"] = {
    "baseUrl": "https://api.anthropic.com/v1",
    "apiKey": "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",
    "api": "anthropic-messages",
    "models": [
        {
            "id": "claude-3-5-sonnet-20241022",
            "name": "Claude 3.5 Sonnet",
            "api": "anthropic-messages",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "reasoning": False,
            "input": ["text", "image"]
        }
    ],
    "timeoutSeconds": 300
}

# 3. Add configuration entry to agent models registry
if "agents" not in config:
    config["agents"] = {}
if "defaults" not in config["agents"]:
    config["agents"]["defaults"] = {}
if "models" not in config["agents"]["defaults"]:
    config["agents"]["defaults"]["models"] = {}

# Initialize Claude model mapping under defaults
config["agents"]["defaults"]["models"]["anthropic/claude-3-5-sonnet-20241022"] = {}

with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print("[SUCCESS] Registered Claude 3.5 Sonnet under the 'anthropic' provider pipeline!")
