import json
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def generate_markdown(findings, filepath):
    """Generate Markdown report"""
    content = "# Lombaohsint Report\n\n"
    content += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    high_risk = [f for f in findings if f.get("risk") == "CRITICAL"]
    medium_risk = [f for f in findings if f.get("risk") == "HIGH"]
    low_risk = [f for f in findings if f.get("risk") == "MEDIUM"]

    content += f"## Summary\n"
    content += f"- Total Findings: {len(findings)}\n"
    content += f"- Critical: {len(high_risk)}\n"
    content += f"- High: {len(medium_risk)}\n"
    content += f"- Medium: {len(low_risk)}\n\n"

    for f in findings:
        if f["type"] == "AI_SUMMARY":
            ai_data = f["data"]
            content += "## AI Digital Twin\n"
            content += f"### Identity\n"
            content += f"- Emails: {', '.join(ai_data.get('digital_twin', {}).get('identity', {}).get('emails', []))}\n"
            content += f"- Phones: {', '.join(ai_data.get('digital_twin', {}).get('identity', {}).get('phones', []))}\n"
            content += f"- Usernames: {', '.join(ai_data.get('digital_twin', {}).get('identity', {}).get('usernames', []))}\n\n"

            content += "### Ethical Insight\n"
            content += f"{ai_data.get('ethical_insight', 'No insight generated.')}\n\n"

            content += "### Unethical Awareness\n"
            content += f"{ai_data.get('unethical_awareness', 'No awareness generated.')}\n\n"
        else:
            content += f"## {f['source']} — {f['type']}\n"
            content += f"**Risk**: {f.get('risk', 'LOW')}\n\n"
            content += "```json\n"
            content += json.dumps(f["data"], indent=2)
            content += "\n```\n\n"

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def generate_html(findings, filepath):
    """Generate HTML report with dark theme"""
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html.jinja2")

    html_content = template.render(
        findings=findings,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        total_findings=len(findings)
    )

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_json(findings, filepath):
    """Generate structured JSON report"""
    report = {
        "target": findings[0].get("target", "unknown") if findings else "unknown",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_findings": len(findings),
        "findings": findings
    }

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
