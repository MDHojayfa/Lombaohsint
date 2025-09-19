import os
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from modules.termux_fixer import fix_termux

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"PREFIX": "/data/data/com.termux/files/usr"}):
        yield

@pytest.fixture
def mock_subprocess_run():
    with patch('subprocess.run') as mock:
        yield mock

def test_fix_termux_not_termux(mock_subprocess_run):
    """Test function does nothing if not in Termux."""
    with patch.dict(os.environ, {"PREFIX": "/usr"}):
        fix_termux()
        mock_subprocess_run.assert_not_called()

def test_fix_termux_installs_packages(mock_env, mock_subprocess_run):
    """Test required packages are installed."""
    mock_subprocess_run.side_effect = lambda *args, **kwargs: None

    fix_termux()

    expected_calls = [
        'pkg install -y python',
        'pkg install -y git',
        'pkg install -y curl',
        'pkg install -y wget',
        'pkg install -y openssl-tool',
        'pkg install -y libffi',
        'pkg install -y clang',
        'pkg install -y make',
        'pkg install -y gcc',
        'pkg install -y proot-distro',
        'pkg install -y tor',
        'pkg install -y nmap',
        'pkg install -y hydra',
        'pkg install -y hashcat',
        'pkg install -y amass',
        'pkg install -y subfinder',
        'pkg install -y shodan-cli'
    ]

    calls = [call.args[0] for call in mock_subprocess_run.call_args_list if 'pkg install' in str(call.args[0])]
    for cmd in expected_calls:
        assert any(cmd in c for c in calls), f"Missing: {cmd}"

def test_fix_termux_installs_ubunutu_chroot(mock_env, mock_subprocess_run):
    """Test Ubuntu chroot is installed and updated."""
    mock_subprocess_run.side_effect = lambda *args, **kwargs: None

    # Simulate Ubuntu not installed
    mock_subprocess_run.return_value.stdout = "debian\n"

    fix_termux()

    # Check for proot-distro install
    install_called = any("proot-distro install ubuntu" in str(call.args[0]) for call in mock_subprocess_run.call_args_list)
    assert install_called, "Ubuntu chroot not installed"

    # Check for update inside chroot
    update_called = any("apt update && apt upgrade -y" in str(call.args[0]) for call in mock_subprocess_run.call_args_list)
    assert update_called, "Ubuntu chroot not updated"

def test_fix_termux_creates_symlink(mock_env, mock_subprocess_run):
    """Test symlink to /storage/emulated/0 is created."""
    with patch('os.path.exists', return_value=True), \
         patch('os.path.islink', return_value=False), \
         patch('os.symlink') as mock_symlink:

        fix_termux()
        mock_symlink.assert_called_once_with('/storage/emulated/0', '/data/data/com.termux/files/home/sdcard')

def test_fix_termux_skips_symlink_if_exists(mock_env, mock_subprocess_run):
    """Test symlink is skipped if already exists."""
    with patch('os.path.exists', return_value=True), \
         patch('os.path.islink', return_value=True):

        with patch('os.symlink') as mock_symlink:
            fix_termux()
            mock_symlink.assert_not_called()

def test_fix_termux_pip_upgrade(mock_env, mock_subprocess_run):
    """Test pip is upgraded."""
    fix_termux()
    pip_upgrade_called = any("pip3 install --upgrade pip" in str(call.args[0]) for call in mock_subprocess_run.call_args_list)
    assert pip_upgrade_called, "pip3 upgrade not called"
