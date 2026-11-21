# 🔗 TreeSense AI — Cloud & Model Resources

This document maintains persistent cloud links for model training checkpoints, datasets, and Google Colab development environments.

---

## ☁️ Google Cloud Links

* **Google Colab Notebook**:  
  [https://colab.research.google.com/drive/1sp3bm9oPkH5PV7c0nrVhDuUsQ4KkPmko?usp=sharing](https://colab.research.google.com/drive/1sp3bm9oPkH5PV7c0nrVhDuUsQ4KkPmko?usp=sharing)
  * *Purpose*: Active training notebook configured for T4 / A100 GPU fine-tuning, SAHI evaluation, and ONNX FP16 export.

* **Google Drive Training Checkpoints & Datasets**:  
  [https://drive.google.com/drive/folders/18zFuIxy7JahatiXlH9362mo2ZDZKvKFZ?usp=sharing](https://drive.google.com/drive/folders/18zFuIxy7JahatiXlH9362mo2ZDZKvKFZ?usp=sharing)
  * *Purpose*: Stores persistent epoch checkpoints (`epoch0.pt` through `epoch50.pt`), `best.pt`, `best.onnx`, and training curves (`results.png`, `confusion_matrix.png`).

---

## 📦 Local Model Artifacts (Synced)
* **PyTorch Weights**: [`models/best.pt`](file:///c:/Users/TANMAY/OneDrive/Desktop/Resume/03_Projects/TreeSense_Imaging/models/best.pt) (YOLOv11m trained for 50 epochs)
* **ONNX Weights**: [`models/best.onnx`](file:///c:/Users/TANMAY/OneDrive/Desktop/Resume/03_Projects/TreeSense_Imaging/models/best.onnx) (FP16 half-precision with dynamic axes)
* **Notebook Source**: [`Training/TreeSense_AI_Training_main.ipynb`](file:///c:/Users/TANMAY/OneDrive/Desktop/Resume/03_Projects/TreeSense_Imaging/Training/TreeSense_AI_Training_main.ipynb)
