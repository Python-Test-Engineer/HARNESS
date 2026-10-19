from datetime import datetime
from pathlib import Path
import random

filename = f"output{random.randint(1000, 9999)}.txt"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

content = (
    "This is Craig West's minimal coding agent\n\n\n"
    + "*" * 50
    + "\n\n"
    + f"HELLO PYDATA {timestamp}\n"
)
Path(filename).write_text(content, encoding="utf-8")
print(f"Wrote {filename}: HELLO PYDATA {timestamp}")
