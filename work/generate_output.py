# This is Craig West's minimal coding agent
#
#
# **************************************************
#

from datetime import datetime
from pathlib import Path
import random


def main():
    number = random.randint(1000, 9999)
    output_path = Path(f"output{number}.txt")
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    prefix = "This is Craig West's minimal coding agent\n\n\n" + "*" * 50 + "\n\n"
    output_path.write_text(prefix + f"HELLO PYDATA - {timestamp}\n", encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
