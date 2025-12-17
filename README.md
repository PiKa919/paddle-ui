# PaddleOCR Studio (paddle-ui)

A modern web-based OCR application powered by PaddleOCR with advanced document parsing capabilities.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.x-green.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## ✨ Features

### 🔍 OCR Mode
- Text detection and recognition with PP-OCRv5
- Multi-language support (11+ languages)
- Image preprocessing (brightness, contrast, saturation, sharpness)
- Bounding box visualization

### 🏗️ Structure Mode (PP-StructureV3)
- Layout detection (text, titles, tables, formulas, charts, seals)
- Table recognition → HTML output
- Formula recognition → LaTeX output
- Chart parsing
- Seal text recognition
- Export to Markdown/JSON

### 🌐 VL Mode (PaddleOCR-VL)
- Vision-Language Model (0.9B parameters)
- 109 languages supported
- SOTA document parsing performance

### 📦 Model Management
- Download/delete models on demand
- Disk usage tracking
- Filter by model type

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Conda (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/paddle-ui.git
cd paddle-ui

# Create conda environment
conda create -n paddle python=3.10 -y
conda activate paddle

# Install dependencies
pip install paddlepaddle paddleocr flask flask-cors pillow opencv-python numpy requests

# Run the application
python app.py
```

Open http://localhost:5000 in your browser.

## 📁 Project Structure

```
paddle-ui/
├── app.py                  # Flask application
├── ocr_engine.py           # PP-OCR wrapper
├── structure_engine.py     # PP-StructureV3 wrapper
├── vl_engine.py            # PaddleOCR-VL wrapper
├── model_manager.py        # Model download/management
├── image_processor.py      # Image preprocessing utilities
├── templates/
│   └── index.html          # Main UI template
└── static/
    ├── css/
    │   └── style.css       # Modern dark theme styles
    └── js/
        └── app.js          # Frontend logic
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ocr` | POST | Basic OCR processing |
| `/api/structure` | POST | PP-StructureV3 document parsing |
| `/api/vl` | POST | PaddleOCR-VL parsing |
| `/api/models` | GET | List available models |
| `/api/models/<id>/download` | POST | Download a model |
| `/api/models/<id>` | DELETE | Delete a model |

## 🖼️ Screenshots

*Coming soon*

## 📝 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PaddlePaddle](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine
- [Flask](https://flask.palletsprojects.com/) - Web framework
