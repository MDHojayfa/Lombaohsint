# Lombaohsint v2.0 Black Edition — Architecture Overview

## Overview

`lombaohsint` is a modular, multi-layered OSINT (Open-Source Intelligence) framework designed for global reconnaissance on any target: email, phone number, username, or keyword.

It runs natively on:
- Kali Linux
- Ubuntu 22.04+
- Debian 12+
- Termux (Android via proot-distro Ubuntu)

The tool is built for **authorized use only** and operates under the principle:  
> *“If you can’t legally scan it, don’t scan it.”*

---

## Core Design Principles

| Principle | Description |
|---------|-------------|
| ✅ **Modular** | Each function (email, phone, username, etc.) is a standalone module. Easy to extend or replace. |
| ✅ **Platform-Agnostic** | Works identically on desktop Linux and Android Termux. |
| ✅ **No Hardcoded Keys** | All API keys are user-provided in `config.yaml`. Never committed. |
| ✅ **Cache-Aware** | Results are cached per target to avoid redundant requests. |
| ✅ **Proxy & Tor Ready** | Supports proxy rotation and Tor circuit switching for anonymity. |
| ✅ **AI-Augmented** | Uses GPT-4o or local LLM to generate threat narratives and remediation advice. |
| ✅ **Ethical by Default** | Requires `--i-am-authorized` flag. No scanning without consent. |

---

## Module Flow Diagram (Text-Based)
