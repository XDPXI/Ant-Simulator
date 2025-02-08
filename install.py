import os

print("Installing required libraries...")
os.system(f"python -m pip install --upgrade pip")
os.system("pip install -r requirements.txt")