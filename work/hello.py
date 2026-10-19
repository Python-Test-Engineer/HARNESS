from datetime import datetime
from random import randint

filename = f"output{randint(1000, 9999)}.txt"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(filename, "w", encoding="utf-8") as output_file:
    output_file.write(f"HELLO PYDATA {timestamp}\n")

print(f"Wrote HELLO PYDATA with timestamp to {filename}")
