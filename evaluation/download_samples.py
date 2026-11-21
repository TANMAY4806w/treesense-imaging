import os
import urllib.request
import cv2
import numpy as np

os.makedirs(r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging\evaluation\test_samples", exist_ok=True)

# Wikimedia public domain aerial forest drone imagery
urls = {
    "aerial_drone_forest_1.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Rainforest_Frying_Pan_River.jpg/1280px-Rainforest_Frying_Pan_River.jpg",
    "aerial_drone_forest_2.jpg": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=1280&q=80"
}

for fname, url in urls.items():
    dest = os.path.join(r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging\evaluation\test_samples", fname)
    if not os.path.exists(dest):
        print(f"Downloading {fname} from {url}...")
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response, open(dest, 'wb') as out_file:
                out_file.write(response.read())
            img = cv2.imread(dest)
            if img is not None:
                print(f"✅ Saved {fname}: {img.shape[1]}x{img.shape[0]} px ({os.path.getsize(dest):,} bytes)")
            else:
                print(f"❌ Failed to decode {fname}")
        except Exception as e:
            print(f"❌ Error downloading {fname}: {e}")
    else:
        print(f"Already exists: {fname}")
