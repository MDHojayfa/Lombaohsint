from pathlib import Path
import os

def get_report_path(target):
    """Convert target to safe filename and return report directory path."""
    safe_name = target.replace("@", "_at_").replace("/", "_").replace("\\", "_")
    return Path("reports") / safe_name

def get_cache_path(target):
    """Return cache directory path for target."""
    safe_name = target.replace("@", "_at_").replace("/", "_").replace("\\", "_")
    return Path("data/cache") / safe_name

def get_absolute_path(relative_path):
    """Resolve path relative to project root."""
    return Path(__file__).parent.parent / relative_path

# Termux-specific path resolution
if "com.termux" in os.environ.get("PREFIX", ""):
    # Override paths for Termux compatibility
    def get_report_path(target):
        safe_name = target.replace("@", "_at_").replace("/", "_").replace("\\", "_")
        return Path("/data/data/com.termux/files/home/lombaohsint/reports") / safe_name

    def get_cache_path(target):
        safe_name = target.replace("@", "_at_").replace("/", "_").replace("\\", "_")
        return Path("/data/data/com.termux/files/home/lombaohsint/data/cache") / safe_name
