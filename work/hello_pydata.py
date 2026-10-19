from datetime import datetime
from pathlib import Path
import random


def main():
    filename = f"output{random.randint(1000, 9999)}.txt"
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    content = (
        "This is Craig West's minimal coding agent\n"
        "\n\n\n\n"
        f"HELLO PYDATA {timestamp}\n"
    )
    Path(filename).write_text(content, encoding="utf-8")
    print(f"Wrote {filename}")


if __name__ == "__main__":
    main()
