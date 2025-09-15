[START]
│
├─ Load ASCII banner from assets/banner.txt
├─ Select random motivational quote from assets/quotes.txt
├─ Print banner + quote to terminal
│
├─ Parse CLI args:
│   ├─ --target [REQUIRED] → string (email/phone/username/keyword)
│   ├─ --level [DEFAULT=BLACK] → GENTLE/NORMAL/BLACK
│   ├─ --i-am-authorized [REQUIRED] → must be present, else EXIT
│   ├─ --export [DEFAULT=all] → md/html/json/all
│   ├─ --verbose → enable debug logs
│   └─ --help → show help and exit
│
├─ Validate: Is --i-am-authorized passed? If not:
│   ├─ Print WARNING: "This tool exposes private data. You are responsible."
│   ├─ Print EXAMPLE: "Use: lombaohsint --target user@example.com --level BLACK --i-am-authorized"
│   └─ Exit(1)
│
├─ Initialize:
│   ├─ logger() → set up log file (data/logs/)
│   ├─ path_manager() → resolve paths across Termux/Linux
│   ├─ config_loader() → load config.yaml
│   └─ validate_target(target) → regex check for email/phone/username/keyword
│
├─ OS Detection:
│   ├─ If Termux detected → call termux_fixer.fix_termux()
│   │   ├─ Install required APT packages if missing
│   │   ├─ Create symlink: ~/sdcard → /storage/emulated/0
│   │   └─ Verify nmap, tor, python3, pip3 installed
│   └─ Else → proceed normally
│
├─ Create directories:
│   ├─ data/cache/email_cache/
│   ├─ data/cache/phone_cache/
│   ├─ data/cache/username_cache/
│   ├─ data/cache/darkweb_cache/
│   ├─ data/logs/
│   ├─ reports/<target>/
│   └─ reports/<target>/artifacts/
│
├─ Load cached breach data from breaches.sqlite (if exists)
│
├─ Initialize proxy_rotator with config.proxy_list and tor settings
│
├─ Initialize api_wrapper with config.api_keys
│
├─ Execute scan modules in sequence:
│   ├─ email_harvest.run(target, level) → returns list[dict]
│   ├─ phone_reversal.run(target, level) → returns list[dict]
│   ├─ username_ghost.run(target, level) → returns list[dict]
│   ├─ darkweb_scrape.run(target, level) → returns list[dict]
│   ├─ git_leak_scan.run(target, level) → returns list[dict]
│   ├─ network_recon.run(target, level) → returns list[dict]
│   ├─ social_deep.run(target, level) → returns list[dict]
│   ├─ credential_crack.run(target, level) → returns list[dict]
│   ├─ ai_synthesis.run(all_findings) → returns dict{digital_twin, ethical, unethical}
│   ├─ proxy_rotator.rotate() → rotate proxy/Tor after each module
│   └─ Append all results into global findings list
│
├─ Merge AI synthesis into findings:
│   ├─ findings.ai_summary = {digital_twin, ethical_insight, unethical_awareness}
│
├─ Generate reports:
│   ├─ report_generator.generate_md(findings, output_dir)
│   ├─ report_generator.generate_html(findings, output_dir)
│   ├─ report_generator.generate_json(findings, output_dir)
│   └─ Copy artifacts (screenshots, leaked files) into reports/<target>/artifacts/
│
├─ Print final summary:
│   ├─ Total findings: X
│   ├─ High-risk items: Y
│   ├─ Report saved to: /path/to/reports/target/
│   └─ "Stay sharp. The truth doesn't wait."
│
└─ [END] — Exit cleanly (code 0)
