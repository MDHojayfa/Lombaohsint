
# Lombaohsint
run this at first
INSTALL SYSTEM DEPENDENCIES (for lxml)

Pip failed on `lxml` because missing system libraries.

Fix it:

### 🔧 On Ubuntu/Kali (proot):
```bash
apt-get install libxml2-dev libxslt-dev python3-dev build-essential -y
```

### 🔧 On Termux:
```bash
pkg install libxml2 libxslt clang make -y
```

Then re-run:
```bash
pip install lxml==5.2.2
```
```markdown
# Lombaohsint v2.0 Black Edition

> **"The only OSINT tool that doesn't just scan — it unmasks."**  
> By MDHojayfa | MDTOOLS

---

## 🔥 Quick Start (30-Second Setup)

Run this on **Kali, Ubuntu, Termux, or Debian**:

```bash
git clone https://github.com/MDHojayfa/Lombaohsint.git
cd Lombaohsint
sudo bash install.sh
sudo source (activate your venv)
sudo pip install -r requirements.txt
```

Then run your first scan:

```bash
lombaohsint --target john.doe@example.com --level BLACK --i-am-authorized
```

✅ That’s it.  
No config. No setup. No dependencies.

---

## 🎯 Supported Targets

Lombaohsint works with:
- ✅ Email: `user@domain.com`
- ✅ Phone: `+919876543210` (Global E.164)
- ✅ Username: `johndoe`
- ✅ Keyword: `john doe`, `acme corp`, `CEO`

All inputs are validated and normalized automatically.

---

## ⚙️ Aggression Levels

| Level | Behavior |
|-------|---------|
| `GENTLE` | Public APIs only — no scraping, no Tor |
| `NORMAL` | Light scanning + Google dorks |
| `BLACK` | Full automation: darkweb, Tor, AI synthesis, cache write |

> Always use `--i-am-authorized` — required for legal operation.

---

## 📦 Features at a Glance

### 1. **Email Intelligence**
- ✔️ Check breaches via HaveIBeenPwned
- ✔️ Scan pastes on PSBDMP
- ✔️ Find secrets in GitHub repos
- ✔️ Verify email via Hunter.io

### 2. **Phone Reversal (232 Countries)**
- ✔️ Validate phone via NumVerify
- ✔️ Get carrier & caller name via Twilio
- ✔️ Detect SIM swap risk via RiskSeal
- ✔️ Reverse identity via Trestle
- ✔️ Web scrape Truecaller (in `BLACK` mode)

### 3. **Username Ghost Hunt**
- ✔️ Maigret scans 1200+ sites
- ✔️ Wayback Machine archive detection
- ✔️ Google Dorking across social platforms

### 4. **Darkweb Scrape**
- ✔️ Uses `.onion` mirrors via Tor
- ✔️ Searches breach forums and paste dumps
- ✔️ Auto-renews Tor circuit

### 5. **Network Recon**
- ✔️ Subdomains via Shodan, Censys, crt.sh
- ✔️ S3 bucket guessing (public exposure)
- ✔️ IP-to-domain correlation

### 6. **Credential Simulation**
- ✔️ Simulates password cracking using common patterns
- ✔️ Checks for domain-based passwords (`company2024!`)
- ✔️ Identifies reuse risk

### 7. **AI Digital Twin**
- ✔️ Generates ethical insight
- ✔️ Predicts attacker behavior
- ✔️ Builds identity graph from all findings

### 8. **Full Report Generation**
- ✔️ Markdown report → clean text
- ✔️ HTML dashboard → interactive UI
- ✔️ JSON schema → SIEM integration

---

## 🛠️ Commands

### Basic Usage
```bash
lombaohsint --target [EMAIL|PHONE|USERNAME] --level [GENTLE/NORMAL/BLACK] --i-am-authorized
```

### Examples
```bash
lombaohsint --target test@example.com --level GENTLE --i-am-authorized
lombaohsint --target +919876543210 --level NORMAL --i-am-authorized
lombaohsint --target johndoe --level BLACK --i-am-authorized
```

### Export Formats
```bash
lombaohsint --target user@domain.com --export md     # Only Markdown
lombaohsint --target user@domain.com --export html # Only HTML
lombaohsint --target user@domain.com --export json # Only JSON
lombaohsint --target user@domain.com --export all  # All formats
```

### Verbose Logging
```bash
lombaohsint --target victim@corp.com --level BLACK --i-am-authorized --verbose
```

---

## 🧩 Configuration (`config.yaml`)

After install, edit `config.yaml` to add API keys:

```yaml
api_keys:
  haveibeenpwned: ""
  numverify: "your_numverify_key"
  twilio: "ACxxxxxxxxx:auth_token"
  hunterio: "your_hunter_io_key"
  intelx: "your_intelx_key"
  shodan: "your_shodan_key"
  censys: "your_id:your_secret"
  github: "ghp_your_github_token"
  trestle: "your_trestle_bearer"
  riskseal: "your_riskseal_apikey"

ai_model: "gpt-4o"
ai_api_key: "your_openai_key"  # For AI summary
use_tor: true                   # Required for darkweb scraping
```

> 💡 You can leave keys empty — the tool will skip those modules.

---

## 🔄 Scripts Included

| Script | Purpose |
|--------|--------|
| `./install.sh` | Auto-detects OS and installs everything |
| `./update.sh` | Pull latest version from GitHub |
| `./cleanup.sh` | Delete logs, reports, cache |
| `./selftest.sh` | Run self-test after installation |

---

## 🖥️ Termux Support (Android)

This tool runs on **unrooted Android** via Termux.

### Install on Termux
```bash
pkg update -y
pkg install git curl wget proot-distro -y
proot-distro install ubuntu
proot-distro login ubuntu -- sh -c "apt update && apt install python3 python3-pip git curl wget -y"
git clone https://github.com/MDHojayfa/Lombaohsint.git
cd Lombaohsint
./install.sh
```

It auto-fixes paths, symlinks `/sdcard`, and sets up Ubuntu chroot.

---

## 📁 Output Location

Reports are saved to:

```
reports/[target]/report.md
reports/[target]/report.html
reports/[target]/report.json
```

Example:  
👉 `reports/john_doe_at_example_com/report.html`

Open in any browser — dark theme included.

---

## 🛡️ Legal & Ethical Warning

> ⚠️ This tool is designed for **authorized security research only**.

You must own the target or have written permission to scan.

Never scan without:

```bash
--i-am-authorized
```

By running this tool, you confirm:
- You are legally authorized to perform reconnaissance
- You accept full responsibility for actions taken
- You comply with GDPR, CFAA, PIPEDA, IT Act 2000, etc.

---

## ✅ Requirements

| System | Required |
|-------|----------|
| Linux (Kali, Ubuntu, Debian) | ✅ Yes |
| Termux (Android) | ✅ Yes |
| Python 3.8+ | ✅ Yes |
| Tor (for darkweb) | ✅ Yes |
| Git | ✅ Yes |
| Internet Access | ✅ Yes |

No GUI needed. Runs headless.

---

## 🌍 Global Coverage

We support **all countries** through:
- `phonenumbers` library (E.164 validation)
- Multi-language social media scanning
- Regional platforms: VK, WeChat, LINE, KakaoTalk, Odnoklassniki, Telegram, WhatsApp
- Automatic language detection in AI engine

From Lagos to Tokyo, Mumbai to São Paulo — we scan them all.

---

## 🧪 Self-Test

After installation, verify everything works:

```bash
./selftest.sh
```

It creates a dummy scan and generates a report.

If successful, you'll see:
```
[✓] Self-test passed!
```

---

## 🔄 Update Tool

Keep up-to-date:

```bash
./update.sh
```

Pulls latest changes from GitHub.

---

## 🗑️ Clean Up

Delete all generated data:

```bash
./cleanup.sh
```

Useful before sharing device or transferring ownership.

---

## 🧰 How It Works (Architecture)

```
main.py
│
├── proxy_rotator → rotates HTTP/Tor connections
├── api_wrapper → handles all external API calls
├── termux_fixer → patches Android environment
│
├── Modules:
│   ├── email_harvest → HIBP, GitHub, Pastebin
│   ├── phone_reversal → NumVerify, Twilio, Truecaller
│   ├── username_ghost → Maigret, Google Dorks
│   ├── darkweb_scrape → .onion sites via Tor
│   ├── git_leak_scan → GitHub secret search
│   ├── network_recon → Shodan, Censys, S3 buckets
│   ├── social_deep → LinkedIn, Twitter, Instagram, VK, WeChat
│   ├── credential_crack → simulates password breach
│   └── ai_synthesis → builds digital twin with GPT-4o
│
└── report_generator → outputs MD/HTML/JSON
```

---

## 🤖 AI-Powered Insights

Every report includes:
- 🧠 Digital Twin: identity, exposure, behavior
- 🛡️ Ethical Insight: what to fix
- ⚔️ Unethical Awareness: how attackers might exploit

Powered by OpenAI's `gpt-4o` or local Llama-3.

---

## 📄 Sample Output

```json
{
  "type": "EMAIL_BREACH",
  "source": "HaveIBeenPwned",
  "data": {
    "name": "Adobe",
    "domain": "adobe.com",
    "pwn_count": 150000000,
    "is_verified": true
  },
  "risk": "HIGH"
}
```

Full reports include screenshots, metadata, and behavioral predictions.

---

## 📂 Folder Structure

```
Lombaohsint/
├── main.py
├── install.sh
├── config.yaml
├── requirements.txt
├── assets/
├── data/
│   ├── cache/
│   └── logs/
├── modules/
├── utils/
├── templates/
├── scripts/
├── tests/
├── docs/
├── reports/
└── README.md
```

All caches are isolated per target.

---

## 🛑 Troubleshooting

### `ModuleNotFoundError: No module named 'tqdm'`
→ Run: `pip3 install tqdm`

### `ERROR: externally-managed-environment`
→ Use virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
```

### `AttributeError: 'NoneType' object has no attribute 'json'`
→ Wait 1 minute — API rate limit triggered.

### `Failed to connect to Tor`
→ Start Tor:
```bash
sudo systemctl start tor
```

For Termux:
```bash
tor &
```

---

## 🌐 Used By

- Red Teams
- SOC Analysts
- Bug Bounty Hunters
- Forensic Investigators
- Cybersecurity Researchers

---

## 📢 Disclaimer

This tool is provided under MIT License.

I am not responsible for misuse.

Use only on targets you are authorized to scan.

> “With great power comes great responsibility.” – Uncle Ben

---

## 📞 Contact

Telegram: [@MDHojayfa](https://t.me/MDHojayfa)  
GitHub: [github.com/MDHojayfa](https://github.com/MDHojayfa)

---

## 🏁 Final Command

```bash
lombaohsint --target YOUR_TARGET_HERE --level BLACK --i-am-authorized
```

Let the truth reveal itself.
```

