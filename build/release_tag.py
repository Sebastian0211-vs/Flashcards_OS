# build/release_tag.py
import subprocess, sys
from pathlib import Path

v = Path("VERSION").read_text(encoding="utf-8").strip()
if not v:
    print("VERSION file is empty")
    sys.exit(1)

tag = f"v{v}"
print(f"Tagging {tag} …")
subprocess.check_call(["git", "tag", tag])
subprocess.check_call(["git", "push", "--tags"])
print(f"✅ Tagged and pushed {tag}")
