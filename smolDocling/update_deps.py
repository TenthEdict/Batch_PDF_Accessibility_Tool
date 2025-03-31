import fileinput
import sys
import os

# Path to the METADATA file
metadata_path = os.path.join(sys.prefix, "lib/python3.13/site-packages/mlx_vlm-0.1.21.dist-info/METADATA")

# Check if the file exists
if not os.path.exists(metadata_path):
    print(f"Could not find {metadata_path}")
    sys.exit(1)

# Replace the scipy requirement
for line in fileinput.input(metadata_path, inplace=True):
    if "Requires-Dist: scipy==1.13.1" in line:
        print("Requires-Dist: scipy>=1.11.4,<1.14.0")
    else:
        print(line, end='')

print("Updated mlx-vlm dependencies to accept scipy 1.11.4")
