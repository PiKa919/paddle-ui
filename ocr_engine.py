"""
PaddleOCR Engine Wrapper
Handles OCR operations with CPU-only mode support
"""
import os
from paddleocr import PaddleOCR
import numpy as np


class OCREngine:
    """Wrapper around PaddleOCR for CPU-only inference"""
    
    # Supported languages and their codes (PaddleOCR 3.x compatible)
    LANGUAGES = {
        'ch': 'Chinese (Simplified)',
        'en': 'English', 
        'chinese_cht': 'Chinese (Traditional)',
        'korean': 'Korean',
        'japan': 'Japanese',
        'ar': 'Arabic',  # Changed from 'arabic' to 'ar'
        'latin': 'Latin',
        'cyrillic': 'Cyrillic',
        'devanagari': 'Devanagari',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ka': 'Kannada',
        'german': 'German',
        'french': 'French',
        'spanish': 'Spanish',
        'italian': 'Italian',
        'portuguese': 'Portuguese',
        'ru': 'Russian',  # Changed from 'russian' to 'ru'
        'hi': 'Hindi',
        'mr': 'Marathi',
    }
    
    # OCR versions available
    OCR_VERSIONS = ['PP-OCRv5', 'PP-OCRv4', 'PP-OCRv3']
    
    def __init__(self, lang='en', ocr_version='PP-OCRv5'):
        """
        Initialize PaddleOCR with CPU-only mode
        
        Args:
            lang: Language code (default: 'en')
            ocr_version: OCR model version (default: 'PP-OCRv5')
        """
        self.lang = lang
        self.ocr_version = ocr_version
        self._ocr = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the PaddleOCR instance"""
        try:
            self._ocr = PaddleOCR(
                lang=self.lang,
                ocr_version=self.ocr_version,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                device='cpu',  # Force CPU-only mode
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PaddleOCR: {e}")
    
    def switch_model(self, lang=None, ocr_version=None):
        """Switch to a different model configuration"""
        if lang:
            self.lang = lang
        if ocr_version:
            self.ocr_version = ocr_version
        self._initialize()
    
    def detect_text(self, image):
        """
        Detect and recognize text in an image
        
        Args:
            image: Image path, URL, or numpy array
            
        Returns:
            dict with 'boxes' (list of bounding boxes) and 'texts' (list of text results)
        """
        result = self._ocr.predict(image)
        
        boxes = []
        texts = []
        
        for res in result:
            # Helper function to get value from result (supports both dict and attribute access)
            def get_value(obj, key, default=None):
                if isinstance(obj, dict) or hasattr(obj, 'keys'):
                    return obj.get(key, default)
                return getattr(obj, key, default)
            
            rec_polys = get_value(res, 'rec_polys')
            rec_texts = get_value(res, 'rec_texts')
            rec_scores = get_value(res, 'rec_scores')
            dt_polys = get_value(res, 'dt_polys')
            
            # Try rec_polys first (PP-OCRv5 format)
            if rec_polys is not None and rec_texts is not None:
                scores = rec_scores if rec_scores is not None else [1.0] * len(rec_texts)
                for i, (poly, text, score) in enumerate(zip(rec_polys, rec_texts, scores)):
                    if poly is not None:
                        poly_list = poly.tolist() if isinstance(poly, np.ndarray) else poly
                        boxes.append({
                            'points': poly_list,
                            'text': text,
                            'confidence': float(score) if score else 1.0
                        })
                        texts.append({
                            'text': text,
                            'confidence': float(score) if score else 1.0
                        })
            # Fallback to dt_polys (alternative format)
            elif dt_polys is not None and rec_texts is not None:
                scores = rec_scores if rec_scores is not None else []
                for i, poly in enumerate(dt_polys):
                    poly_list = poly.tolist() if isinstance(poly, np.ndarray) else poly
                    text = rec_texts[i] if i < len(rec_texts) else ''
                    score = scores[i] if i < len(scores) else 1.0
                    boxes.append({
                        'points': poly_list,
                        'text': text,
                        'confidence': float(score)
                    })
                    texts.append({
                        'text': text,
                        'confidence': float(score)
                    })
        
        return {
            'boxes': boxes,
            'texts': texts,
            'full_text': ' '.join([t['text'] for t in texts])
        }
    
    def get_available_languages(self):
        """Return list of available languages"""
        return self.LANGUAGES
    
    def get_available_versions(self):
        """Return list of available OCR versions"""
        return self.OCR_VERSIONS
