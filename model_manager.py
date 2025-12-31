"""
Model Manager for PaddleOCR
Handles model discovery, download, and deletion
"""
import os
import shutil
import json
from pathlib import Path


class ModelManager:
    """Manages PaddleOCR model downloads and storage"""
    
    # Default PaddleOCR models directory
    DEFAULT_MODEL_DIR = os.path.expanduser("~/.paddleocr")
    
    # Model registry with download URLs
    MODEL_REGISTRY = {
        # Detection Models
        'PP-OCRv5_server_det': {
            'name': 'PP-OCRv5 Server Detection',
            'type': 'detection',
            'version': 'v5',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_server_det_infer.tar',
            'size_mb': 110,
        },
        'PP-OCRv5_mobile_det': {
            'name': 'PP-OCRv5 Mobile Detection',
            'type': 'detection', 
            'version': 'v5',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_mobile_det_infer.tar',
            'size_mb': 4,
        },
        'PP-OCRv4_server_det': {
            'name': 'PP-OCRv4 Server Detection',
            'type': 'detection',
            'version': 'v4',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv4_server_det_infer.tar',
            'size_mb': 110,
        },
        'PP-OCRv4_mobile_det': {
            'name': 'PP-OCRv4 Mobile Detection',
            'type': 'detection',
            'version': 'v4',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv4_mobile_det_infer.tar',
            'size_mb': 4,
        },
        'PP-OCRv3_mobile_det': {
            'name': 'PP-OCRv3 Mobile Detection',
            'type': 'detection',
            'version': 'v3',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_det_infer.tar',
            'size_mb': 2,
        },
        # Recognition Models - Chinese
        'PP-OCRv5_server_rec_ch': {
            'name': 'PP-OCRv5 Server Recognition (Chinese)',
            'type': 'recognition',
            'version': 'v5',
            'language': 'ch',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_server_rec_infer.tar',
            'size_mb': 80,
        },
        'PP-OCRv5_mobile_rec_ch': {
            'name': 'PP-OCRv5 Mobile Recognition (Chinese)',
            'type': 'recognition',
            'version': 'v5',
            'language': 'ch',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv5_mobile_rec_infer.tar',
            'size_mb': 10,
        },
        # Recognition Models - English
        'PP-OCRv4_mobile_rec_en': {
            'name': 'PP-OCRv4 Mobile Recognition (English)',
            'type': 'recognition',
            'version': 'v4',
            'language': 'en',
            'url': 'https://paddleocr.bj.bcebos.com/PP-OCRv4/english/en_PP-OCRv4_rec_infer.tar',
            'size_mb': 10,
        },
        # Multilingual Recognition Models
        'PP-OCRv3_rec_korean': {
            'name': 'PP-OCRv3 Recognition (Korean)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'korean',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/korean_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_japan': {
            'name': 'PP-OCRv3 Recognition (Japanese)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'japan',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/japan_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_arabic': {
            'name': 'PP-OCRv3 Recognition (Arabic)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'arabic',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/arabic_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_devanagari': {
            'name': 'PP-OCRv3 Recognition (Hindi/Devanagari)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'devanagari',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/devanagari_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_latin': {
            'name': 'PP-OCRv3 Recognition (Latin)',
            'type': 'recognition',
            'version': 'v3', 
            'language': 'latin',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/latin_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_cyrillic': {
            'name': 'PP-OCRv3 Recognition (Cyrillic)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'cyrillic',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/cyrillic_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_tamil': {
            'name': 'PP-OCRv3 Recognition (Tamil)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'ta',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/ta_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        'PP-OCRv3_rec_telugu': {
            'name': 'PP-OCRv3 Recognition (Telugu)',
            'type': 'recognition',
            'version': 'v3',
            'language': 'te',
            'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/te_PP-OCRv3_mobile_rec_infer.tar',
            'size_mb': 12,
        },
        # Angle Classification
        'PP-OCRv3_cls': {
            'name': 'PP-OCRv3 Angle Classification',
            'type': 'classification',
            'version': 'v3',
            'url': 'https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar',
            'size_mb': 2,
        },
    }
    
    def __init__(self, model_dir=None):
        """
        Initialize the model manager
        
        Args:
            model_dir: Custom model directory (default: ~/.paddleocr)
        """
        self.model_dir = Path(model_dir or self.DEFAULT_MODEL_DIR)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def get_model_list(self):
        """
        Get list of all models with their installation status
        
        Returns:
            List of model dictionaries with 'installed' status
        """
        models = []
        installed_models = self._get_installed_models()
        
        for model_id, info in self.MODEL_REGISTRY.items():
            model = {
                'id': model_id,
                'installed': model_id in installed_models,
                **info
            }
            if model['installed']:
                model['installed_path'] = str(installed_models.get(model_id, ''))
            models.append(model)
        
        return models
    
    def _get_installed_models(self):
        """Scan model directory for installed models"""
        installed = {}
        
        if not self.model_dir.exists():
            return installed
        
        # Check for model directories in the paddleocr cache
        for item in self.model_dir.rglob('*'):
            if item.is_dir():
                # Check if this directory contains model files
                has_pdmodel = any(item.glob('*.pdmodel')) or any(item.glob('inference.pdmodel'))
                has_pdiparams = any(item.glob('*.pdiparams')) or any(item.glob('inference.pdiparams'))
                
                if has_pdmodel or has_pdiparams:
                    # Try to match it to a known model
                    dir_name = item.name.lower()
                    for model_id in self.MODEL_REGISTRY:
                        model_id_lower = model_id.lower().replace('_', '')
                        if model_id_lower in dir_name.replace('_', '').replace('-', ''):
                            installed[model_id] = str(item)
                            break
        
        return installed
    
    def download_model(self, model_id, callback=None):
        """
        Download a model from the registry
        
        Args:
            model_id: Model ID from the registry
            callback: Optional progress callback function(downloaded, total)
            
        Returns:
            Path to downloaded model directory
        """
        import requests
        import tarfile
        import tempfile
        
        if model_id not in self.MODEL_REGISTRY:
            raise ValueError(f"Unknown model ID: {model_id}")
        
        model_info = self.MODEL_REGISTRY[model_id]
        url = model_info['url']
        
        # Create model-specific directory
        model_path = self.model_dir / model_id
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Download the tar file
        with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp_file:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
                downloaded += len(chunk)
                if callback:
                    callback(downloaded, total_size)
            
            tmp_path = tmp_file.name
        
        # Extract the tar file
        try:
            with tarfile.open(tmp_path, 'r') as tar:
                tar.extractall(path=model_path)
        finally:
            os.unlink(tmp_path)
        
        return str(model_path)
    
    def delete_model(self, model_id):
        """
        Delete an installed model
        
        Args:
            model_id: Model ID to delete
            
        Returns:
            True if deleted successfully
        """
        installed = self._get_installed_models()
        
        if model_id not in installed:
            raise ValueError(f"Model not installed: {model_id}")
        
        model_path = Path(installed[model_id])
        
        if model_path.exists():
            shutil.rmtree(model_path)
            return True
        
        return False
    
    def get_model_info(self, model_id):
        """Get detailed information about a model"""
        if model_id not in self.MODEL_REGISTRY:
            return None
        
        installed = self._get_installed_models()
        info = dict(self.MODEL_REGISTRY[model_id])
        info['id'] = model_id
        info['installed'] = model_id in installed
        
        if info['installed']:
            info['installed_path'] = installed[model_id]
        
        return info
    
    def get_disk_usage(self):
        """Get total disk usage of installed models"""
        total_size = 0
        
        if self.model_dir.exists():
            for item in self.model_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        
        return total_size
