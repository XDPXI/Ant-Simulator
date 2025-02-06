import os

libraries = "numpy pygame screeninfo perlin-noise"

print("Installing required libraries...")
os.system(f"python -m pip install --upgrade pip {libraries}")
