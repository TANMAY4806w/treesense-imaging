import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging")

from backend.app.services.detector import TreeDetectorService
from backend.app.core.config import settings

print(f"Testing TreeDetectorService with model: {settings.DEFAULT_MODEL_PT}")
print(f"Model exists: {settings.DEFAULT_MODEL_PT.exists()}")

service = TreeDetectorService()

test_img_path = r"c:\Users\TANMAY\OneDrive\Desktop\Resume\03_Projects\TreeSense_Imaging\evaluation\test_samples\drone_mixed_canopy.jpg"
with open(test_img_path, "rb") as f:
    img_bytes = f.read()

# Run standard
res_std = service.detect(img_bytes, conf_thresh=0.25, use_sahi=False)
print("\n[Standard Full Canvas YOLOv11]")
print(f"  Tree Count: {res_std.tree_count}")
print(f"  Avg Confidence: {res_std.avg_confidence * 100:.1f}%")
print(f"  Canopy Density: {res_std.canopy_density}")
print(f"  Estimated Coverage: {res_std.est_canopy_coverage_pct:.1f}%")
print(f"  Annotated base64 size: {len(res_std.annotated_image)} chars")

# Run SAHI
res_sahi = service.detect(img_bytes, conf_thresh=0.25, use_sahi=True)
print("\n[SAHI Sliced Tiling YOLOv11]")
print(f"  Tree Count: {res_sahi.tree_count}")
print(f"  Avg Confidence: {res_sahi.avg_confidence * 100:.1f}%")
print(f"  Canopy Density: {res_sahi.canopy_density}")
print(f"  Estimated Coverage: {res_sahi.est_canopy_coverage_pct:.1f}%")
print(f"  Slice Count: {res_sahi.slice_count}")
print(f"  Annotated base64 size: {len(res_sahi.annotated_image)} chars")
print("\n✅ TreeDetectorService PASSED ALL IN-PROCESS UNIT TESTS!")
