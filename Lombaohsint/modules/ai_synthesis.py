import json
import time
import requests
from utils.logger import logging
from utils.obfuscation import get_random_ua

def run(findings, config):
    """
    Generates AI-powered digital twin, ethical insight, and unethical awareness.
    Uses GPT-4o via API or local Llama-3 model.
    """
    result = {
        "digital_twin": {},
        "ethical_insight": "",
        "unethical_awareness": ""
    }

    if not config.get("ai_summary_enabled", False):
        return result

    # Extract data
    emails = [f["data"].get("email") for f in findings if f.get("type") == "EMAIL_BREACH"]
    phones = [f["data"].get("number") for f in findings if f.get("type") == "NUMVERIFY_LOOKUP"]
    usernames = [f["data"].get("url", "").split("/")[-1] for f in findings if f.get("type") in ["USERNAME_FOUND", "GITHUB_SOCIAL"]]
    breaches = [f["data"].get("name") for f in findings if f.get("type") == "EMAIL_BREACH"]
    exposed_secrets = [f["data"].get("file") for f in findings if f.get("type") == "GITHUB_SECRET"]
    social_profiles = [f["data"].get("url") for f in findings if f.get("type") in ["LINKEDIN_PROFILE", "TWITTER_PROFILE", "INSTAGRAM_PROFILE", "FACEBOOK_PUBLIC"]]

    # Build digital twin
    digital_twin = {
        "identity": {
            "emails": list(set(emails)),
            "phones": list(set(phones)),
            "usernames": list(set(usernames))
        },
        "exposure": {
            "breaches": len(breaches),
            "secrets": len(exposed_secrets),
            "social_profiles": len(social_profiles)
        },
        "behavior": {
            "tech_exposure": "High" if exposed_secrets else "Low",
            "public_presence": "Active" if social_profiles else "Minimal"
        }
    }

    # Build prompt
    prompt = f"""
You are an AI security analyst. Analyze the following digital footprint:

Emails: {emails}
Phones: {phones}
Usernames: {usernames}
Breaches: {breaches}
Exposed Secrets: {exposed_secrets}
Social Profiles: {social_profiles}

Generate two responses:

1. Ethical Insight: What should the target do to protect themselves? Be concise, actionable.
2. Unethical Awareness: How might an attacker exploit this information? Describe tactics without giving instructions.

Format output as JSON with keys: "ethical_insight" and "unethical_awareness".
Do not include any other text.
"""

    # Use local model if configured
    if config.get("ai_local_mode", False):
        try:
            payload = {
                "model": config["ai_local_model_name"],
                "prompt": prompt,
                "stream": False
            }
            resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "")
                try:
                    parsed = json.loads(response_text)
                    result["ethical_insight"] = parsed.get("ethical_insight", "")
                    result["unethical_awareness"] = parsed.get("unethical_awareness", "")
                except:
                    # Fallback parsing
                    lines = response_text.splitlines()
                    for line in lines:
                        if "ethical_insight" in line.lower():
                            result["ethical_insight"] = line.split(":", 1)[1].strip().strip('"')
                        if "unethical_awareness" in line.lower():
                            result["unethical_awareness"] = line.split(":", 1)[1].strip().strip('"')
                result["digital_twin"] = digital_twin
                return result
        except Exception as e:
            logging.warning(f"Local LLM failed: {e}")

    # Fall back to OpenAI GPT-4o
    if config.get("ai_api_key"):
        try:
            headers = {
                "Authorization": f"Bearer {config['ai_api_key']}",
                "Content-Type": "application/json",
                "User-Agent": get_random_ua()
            }
            payload = {
                "model": config["ai_model"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": config.get("ai_max_tokens", 1500),
                "temperature": config.get("ai_temperature", 0.7)
            }
            resp = requests.post(config["ai_endpoint"], headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()

                # Parse JSON from response
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != -1:
                    json_str = content[start:end]
                    parsed = json.loads(json_str)
                    result["ethical_insight"] = parsed.get("ethical_insight", "")
                    result["unethical_awareness"] = parsed.get("unethical_awareness", "")

                result["digital_twin"] = digital_twin
                return result
        except Exception as e:
            logging.warning(f"GPT-4o AI synthesis failed: {e}")

    # Fallback static message
    result["digital_twin"] = digital_twin
    result["ethical_insight"] = "Review all exposed credentials. Enable MFA everywhere. Monitor for new breaches."
    result["unethical_awareness"] = "Attackers may combine breached passwords with social profiles to launch targeted phishing or credential stuffing attacks."

    return result
