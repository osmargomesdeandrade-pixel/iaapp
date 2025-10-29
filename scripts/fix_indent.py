from pathlib import Path

p = Path("demo_generated/demo_ai/app.py")
s = p.read_text()
# Replace leading 5 spaces with 4 on lines
lines = []
for line in s.splitlines(True):
    if line.startswith("     "):
        lines.append("    " + line[5:])
    else:
        lines.append(line)

p.write_text("".join(lines))
print("fixed")
