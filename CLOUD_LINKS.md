# 🔗 TreeSense AI — Cloud & Model Resources

This document maintains persistent cloud links for live production deployments, model training checkpoints, datasets, and development environments.

---

## 🚀 Live Production Deployments

* **Production Web Console (Vercel)**:  
  [https://treesense-imaging-neon.vercel.app/](https://treesense-imaging-neon.vercel.app/)  
  * *Purpose*: Real-time web application dashboard with 1-click sample orthomosaics, atmospheric radar, and spectral canvas.

* **Production AI Microservice (Render)**:  
  [https://treesense-imaging.onrender.com/](https://treesense-imaging.onrender.com/)  
  * *API Health Endpoint*: [https://treesense-imaging.onrender.com/health](https://treesense-imaging.onrender.com/health)  
  * *Interactive Swagger Docs*: [https://treesense-imaging.onrender.com/docs](https://treesense-imaging.onrender.com/docs)  
  * *Purpose*: Containerized FastAPI ASGI server running lightweight ONNX Runtime inference (<150MB RAM).

* **24/7 Keep-Alive Automation (GitHub Actions)**:  
  [https://github.com/TANMAY4806w/treesense-imaging/actions](https://github.com/TANMAY4806w/treesense-imaging/actions)  
  * *Purpose*: Runs every 14 minutes to ping `/health`, preventing free-tier instance idle spin-downs.

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
