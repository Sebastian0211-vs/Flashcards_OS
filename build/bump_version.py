import sys
from pathlib import Path

version_path = Path("VERSION")
M, m, p = map(int, version_path.read_text().strip().split("."))

if len(sys.argv) < 2:
    print("usage: bump_version.py [patch|minor|major]")
    sys.exit(1)

t = sys.argv[1]
if t == "patch":
    p += 1
elif t == "minor":
    m, p = m + 1, 0
elif t == "major":
    M, m, p = M + 1, 0
else:
    print("unknown type:", t)
    sys.exit(1)

new_ver = f"{M}.{m}.{p}"
version_path.write_text(new_ver)
print(new_ver)
