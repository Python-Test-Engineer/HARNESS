import random
import subprocess
import datetime
import os

# Generate random 4-digit number between 1000 and 9999
xxxx = random.randint(1000, 9999)
filename = f"test{xxxx}.py"

# Write the hello world script with datetime stamp output
script_content = '''import datetime

print(f"Hello World! - {datetime.datetime.now()}")
'''

with open(filename, "w") as f:
    f.write(script_content)

print(f"Created {filename}")

# Run the script 3 times and save output to a file
output_file = f"output_test{xxxx}.txt"
with open(output_file, "w") as out:
    out.write(f"Output of {filename} run 3 times:\n")
    out.write("=" * 40 + "\n")
    for i in range(1, 4):
        result = subprocess.run(["python", filename], capture_output=True, text=True)
        line = f"Run {i}: {result.stdout.strip()}"
        print(line)
        out.write(line + "\n")

print(f"\nOutput saved to {output_file}")
print(f"Contents of {output_file}:")
print("-" * 40)
with open(output_file) as out:
    print(out.read())
