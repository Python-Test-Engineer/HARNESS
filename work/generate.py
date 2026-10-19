from datetime import datetime
from pathlib import Path
import random

output_path = Path(f"output{random.randint(1000, 9999)}.txt")
timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

content = (
    "This is Craig West's minimal coding agent\n"
    "\n"
    "\n"
    + "*" * 50
    + "\n\n"
    + f"HELLO PYDATA {timestamp}\n"
)
output_path.write_text(content, encoding="utf-8")
print(f"Wrote {output_path}")
