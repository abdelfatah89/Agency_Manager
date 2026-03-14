import urllib.request
import os

url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "Amiri-Regular.ttf")
os.makedirs(os.path.dirname(dest), exist_ok=True)
urllib.request.urlretrieve(url, dest)
print(f"Downloaded to {dest}")
print(f"File size: {os.path.getsize(dest)} bytes")
