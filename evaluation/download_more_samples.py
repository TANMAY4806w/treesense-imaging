import os
import urllib.request
import cv2

dest_dir = r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging\evaluation\test_samples"

# Top down drone forest photos on Unsplash
urls = {
    "drone_canopy_topdown.jpg": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1280&q=80", # beach/palm
    "aerial_pine_forest.jpg": "https://images.unsplash.com/photo-1511497584788-87676104235f?w=1280&q=80", # dense forest top down
    "drone_mixed_canopy.jpg": "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=1280&q=80"  # top down trees
}

for fname, url in urls.items():
    dest = os.path.join(dest_dir, fname)
    if not os.path.exists(dest):
        print(f"Downloading {fname}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'TreeSenseEvaluation/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp, open(dest, 'wb') as f:
                f.write(resp.read())
            img = cv2.imread(dest)
            if img is not None:
                print(f"✅ Saved {fname}: {img.shape[1]}x{img.shape[0]} px")
        except Exception as e:
            print(f"❌ Error {fname}: {e}")
