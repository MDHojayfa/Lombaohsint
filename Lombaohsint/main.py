#!/usr/bin/env python3
# main.py — Lombaohsint v2.0 Black Edition
# Author: MDHojayfa | MDTOOLS
# License: MIT — Use freely. Own the consequences.
# DO NOT RUN WITHOUT --i-am-authorized

import sys
import os
import json
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Import internal utilities
from utils.logger import setup_logger
from utils.path_manager import get_report_path, get_cache_path
from utils.validator import validate_target
from utils.progress import show_spinner, progress_bar
from utils.obfuscation import get_random_ua

# Import modules
from modules.email_harvest import run as email_harvest
from modules.phone_reversal import run as phone_reversal
from modules.username_ghost import run as username_ghost
from modules.darkweb_scrape import run as darkweb_scrape
from modules.git_leak_scan import run as git_leak_scan
from modules.network_recon import run as network_recon
from modules.social_deep import run as social_deep
from modules.credential_crack import run as credential_crack
from modules.ai_synthesis import run as ai_synthesis
from modules.proxy_rotator import ProxyRotator
from modules.api_wrapper import APIWrapper
from modules.report_generator import generate_markdown, generate_html, generate_json
from modules.termux_fixer import fix_termux


def load_banner():
    """Load ASCII banner from assets/banner.txt"""
    banner_path = Path("assets/banner.txt")
    if not banner_path.exists():
        print("[!] ERROR: banner.txt missing. Corrupted install.")
        sys.exit(1)
    with open(banner_path, "r", encoding="utf-8") as f:
        return f.read()


def load_quotes():
    """Load motivational quotes from assets/quotes.txt"""
    quote_path = Path("assets/quotes.txt")
    if not quote_path.exists():
        return ["Stay sharp. The truth doesn't wait."]
    with open(quote_path, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes if quotes else ["Stay sharp. The truth doesn't wait."]


def parse_args():
    parser = argparse.ArgumentParser(
        description="lombaohsint — Unrestricted OSINT Apocalypse by MDHojayfa (MDTOOLS)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--target", required=True, help="Target: email, phone, username, or keyword")
    parser.add_argument("--level", choices=["GENTLE", "NORMAL", "BLACK"], default="BLACK",
                        help="Aggression level: GENTLE (public APIs only), NORMAL (light scraping), BLACK (full automation)")
    parser.add_argument("--i-am-authorized", action="store_true",
                        help="REQUIRED: Confirm you have legal authorization to scan this target")
    parser.add_argument("--export", choices=["md", "html", "json", "all"], default="all",
                        help="Export format: md, html, json, or all (default)")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def main():
    args = parse_args()

    # --- SECURITY CHECK ---
    if not args.i_am_authorized:
        print("\033[1;31m[!] ERROR: You must pass --i-am-authorized to confirm legal responsibility.\033[0m")
        print("\033[1;33m[!] This tool can expose private data. You are responsible for your actions.\033[0m")
        print("\033[1;36m[!] Example: lombaohsint --target user@example.com --level BLACK --i-am-authorized\033[0m")
        sys.exit(1)

    # --- LOAD RESOURCES ---
    print("\033[1;31m" + load_banner() + "\033[0m")
    quote = random.choice(load_quotes())
    print(f"\033[1;33m{quote}\033[0m\n")

    # --- INITIALIZE LOGGING ---
    log_file = "data/logs/lombaohsint_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    setup_logger(args.verbose, log_file)
    logger = logging.getLogger("lombaohsint")

    # --- VALIDATE TARGET ---
    target = args.target.strip()
    if not validate_target(target):
        logger.error(f"Invalid target format: {target}")
        print("\033[1;31m[!] ERROR: Target must be a valid email, phone number, username, or keyword.\033[0m")
        sys.exit(1)

    logger.info(f"Starting scan for target: {target} | Level: {args.level}")

    # --- SET UP PATHS ---
    report_dir = get_report_path(target)
    cache_dir = get_cache_path(target)
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs("data/cache/email_cache", exist_ok=True)
    os.makedirs("data/cache/phone_cache", exist_ok=True)
    os.makedirs("data/cache/username_cache", exist_ok=True)
    os.makedirs("data/cache/darkweb_cache", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs(f"{report_dir}/artifacts", exist_ok=True)

    # --- DETECT AND FIX TERMUX ENVIRONMENT ---
    if "com.termux" in os.environ.get("PREFIX", ""):
        logger.info("Detected Termux environment. Applying fixes...")
        fix_termux()

    # --- LOAD CONFIG ---
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.critical("config.yaml not found. Run install.sh first.")
        print("\033[1;31m[!] ERROR: config.yaml is missing. Run install.sh to set up the tool.\033[0m")
        sys.exit(1)

    try:
        import yaml
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.critical(f"Failed to load config.yaml: {e}")
        print(f"\033[1;31m[!] ERROR: Failed to load config.yaml: {e}\033[0m")
        sys.exit(1)

    # --- INITIALIZE PROXY ROTATOR & API WRAPPER ---
    proxy_rotator = ProxyRotator(config)
    api_wrapper = APIWrapper(config)

    # --- SCAN MODULES ---
    findings = []

    modules = [
        ("email_harvest", email_harvest),
        ("phone_reversal", phone_reversal),
        ("username_ghost", username_ghost),
        ("darkweb_scrape", darkweb_scrape),
        ("git_leak_scan", git_leak_scan),
        ("network_recon", network_recon),
        ("social_deep", social_deep),
        ("credential_crack", credential_crack),
    ]

    print(f"\033[1;36m[+] Target: {target}\033[0m")
    print(f"\033[1;36m[+] Mode: {args.level}\033[0m")
    print(f"\033[1;33m[>] Initializing reconnaissance swarm...\033[0m")
    progress_bar(15, delay=0.05)

    for module_name, module_func in modules:
        print(f"\033[1;34m[>] Running {module_name}...\033[0m")
        try:
            with show_spinner(f"Scanning via {module_name}"):
                result = module_func(target, args.level, config, api_wrapper, proxy_rotator)
                if result:
                    findings.extend(result)
                    logger.info(f"[SUCCESS] {module_name} returned {len(result)} findings")
                else:
                    logger.info(f"[INFO] {module_name} returned no findings")
        except Exception as e:
            logger.error(f"[FAILED] {module_name} threw exception: {str(e)}")
            print(f"\033[1;31m[!] {module_name} failed: {e}\033[0m")

        # Rotate proxy after each module (if enabled)
        if config.get("proxy_rotation_enabled", False):
            proxy_rotator.rotate()

        progress_bar(3, delay=0.05)

    # --- AI SYNTHESIS ---
    print(f"\033[1;35m[>] Generating AI-powered digital twin...\033[0m")
    try:
        ai_result = ai_synthesis(findings, config)
        findings.append({"type": "AI_SUMMARY", "source": "AI_SYNTHESIS", "data": ai_result})
        logger.info("AI synthesis completed successfully")
    except Exception as e:
        logger.error(f"AI synthesis failed: {e}")
        print(f"\033[1;31m[!] AI synthesis failed: {e}\033[0m")
        print(f"\033[1;33m[!] Continuing without AI insights...\033[0m")

    # --- GENERATE REPORTS ---
    print(f"\033[1;32m[>] Generating reports...\033[0m")
    try:
        if args.export in ["md", "all"]:
            generate_markdown(findings, report_dir / "report.md")
        if args.export in ["html", "all"]:
            generate_html(findings, report_dir / "report.html")
        if args.export in ["json", "all"]:
            generate_json(findings, report_dir / "report.json")
        logger.info(f"Reports generated in {report_dir}")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        print(f"\033[1;31m[!] Report generation failed: {e}\033[0m")

    # --- FINAL SUMMARY ---
    total_findings = len([f for f in findings if f["type"] != "AI_SUMMARY"])
    high_risk = len([f for f in findings if f.get("risk", "") == "HIGH"])

    print(f"\n\033[1;32m[✓] Scan complete!\033[0m")
    print(f"\033[1;36m[+] Total findings: {total_findings}\033[0m")
    print(f"\033[1;31m[!] High-risk exposures: {high_risk}\033[0m")
    print(f"\033[1;36m[+] Reports saved to: \033[1;37m{report_dir}\033[0m")

    if high_risk > 0:
        print(f"\033[1;31m[⚡] CRITICAL: Attack surface fully mapped. Immediate action recommended.\033[0m")
    else:
        print(f"\033[1;32m[✅] No critical exposures found. Target appears clean.\033[0m")

    print(f"\033[1;33m[!] Remember: Power without responsibility is chaos.\033[0m")


if __name__ == "__main__":
    main()
