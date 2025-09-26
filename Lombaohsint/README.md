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


