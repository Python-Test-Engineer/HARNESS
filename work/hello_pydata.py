from datetime import datetime
from random import randint
from pathlib import Path

filename = f"output{randint(1000, 9999)}.txt"
message = f"HELLO PYDATA {datetime.now().isoformat(sep=' ', timespec='seconds')}\n"

Path(filename).write_text(message, encoding="utf-8")
print(f"Wrote {message.strip()!r} to {filename}")
