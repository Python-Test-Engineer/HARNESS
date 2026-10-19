import random
from datetime import datetime

# Generate a random number between 1000 and 9999
number = random.randint(1000, 9999)

# Build the output filename
filename = f"output{number}.txt"

# Create a date-time stamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Write the message with the timestamp to the file
with open(filename, "w") as f:
    f.write(f"HELLO PYDATA {timestamp}\n")

print(f"Wrote to {filename}")
