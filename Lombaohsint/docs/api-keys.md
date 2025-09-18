# Lombaohsint v2.0 — API Key Guide

> 🔐 Store all keys in `config.yaml`. Never commit them to Git.  
> Use `--i-am-authorized` to confirm legal use.

---

## 1. HaveIBeenPwned (HIBP)

- **Purpose**: Check if email/phone was leaked in public breaches
- **URL**: https://haveibeenpwned.com/API/v3
- **Key Required**: ❌ No key needed for basic use — anonymous access allowed
- **Rate Limit**: 1 request per second (unauthenticated)
- **Usage**: Leave empty in config → tool uses anonymous mode
- **Pro Tip**: For higher limits, subscribe at: https://haveibeenpwned.com/API/Key

```yaml
api_keys:
  haveibeenpwned: ""  # Leave blank for anonymous access
