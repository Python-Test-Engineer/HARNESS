#!/usr/bin/env python3
"""Write HELLO PYDATA and a timestamp to a randomly named output file."""

from datetime import datetime
from pathlib import Path
import random


def main():
    filename = f"output{random.randint(1000, 9999)}.txt"
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    content = (
        "This is Craig West's minimal coding agent\n"
        "\n\n"
        f"{'*' * 50}\n"
        "\n"
        f"HELLO PYDATA {timestamp}\n"
    )
    Path(filename).write_text(content, encoding="utf-8")
    print(f"HELLO PYDATA {timestamp}")
    print(f"Wrote {filename}")


if __name__ == "__main__":
    main()
