# 🔗 TreeSense AI — Cloud & Model Resources

This document maintains persistent cloud links for model training checkpoints, datasets, and Google Colab development environments.

---

## ☁️ Google Cloud Links

* **Google Colab Notebook**:  
  [https://colab.research.google.com/drive/1sp3bm9oPkH5PV7c0nrVhDuUsQ4KkPmko?usp=sharing](https://colab.research.google.com/drive/1sp3bm9oPkH5PV7c0nrVhDuUsQ4KkPmko?usp=sharing)
  * *Purpose*: Active training notebook configured for T4 / A100 GPU fine-tuning, SAHI evaluation, and ONNX FP16 export.

* **Google Drive Training Checkpoints & Datasets**:  
  [https://drive.google.com/drive/folders/18zFuIxy7JahatiXlH9362mo2ZDZKvKFZ?usp=sharing](https://drive.google.com/drive/folders/18zFuIxy7JahatiXlH9362mo2ZDZKvKFZ?usp=sharing)
  * *Direct Checkpoints Run Folder (`yolo11_treesense_v6`)*: [https://drive.google.com/drive/folders/1wc8SxmVeggDmrtjxjCQXPVdZ3XtAk9r](https://drive.google.com/drive/folders/1wc8SxmVeggDmrtjxjCQXPVdZ3XtAk9r)
  * *Direct Weights Folder (`best.pt`, `epoch0-40.pt`, `last.pt`)*: [https://drive.google.com/drive/folders/12J6uThbjw9ZQH1A_XoHfE5B4AFbhfVFo](https://drive.google.com/drive/folders/12J6uThbjw9ZQH1A_XoHfE5B4AFbhfVFo)
  * *Purpose*: Stores persistent epoch checkpoints (`epoch0.pt` through `epoch40.pt`, `last.pt`), `best.pt`, `best.onnx`, and training curves (`results.png`, `confusion_matrix.png`, `BoxPR_curve.png`).

---

## 📦 Local Model Artifacts (Synced)
* **PyTorch Weights**: [`models/best.pt`](file:///c:/Users/TANMAY/OneDrive/Desktop/Resume/03_Projects/TreeSense_Imaging/models/best.pt) (YOLOv11m trained for 50 epochs)
* **ONNX Weights**: [`models/best.onnx`](file:///c:/Users/TANMAY/OneDrive/Desktop/Resume/03_Projects/TreeSense_Imaging/models/best.onnx) (FP16 half-precision with dynamic axes)
* **Notebook Source**: [`Training/TreeSense_AI_Training_main.ipynb`](file:///c:/Users/TANMAY/OneDrive/Desktop/Resume/03_Projects/TreeSense_Imaging/Training/TreeSense_AI_Training_main.ipynb)
