"""
PaddleOCR-VL Engine Wrapper
Vision-Language Model for multilingual document parsing
"""
import os
import tempfile
import json
from paddleocr import PaddleOCRVL
import numpy as np


class VLEngine:
    """Wrapper around PaddleOCR-VL for vision-language document parsing"""
    
    # Supported languages (109 total)
    SUPPORTED_LANGUAGES = [
        'Chinese', 'English', 'Japanese', 'Korean', 'Arabic', 'Russian',
        'Hindi', 'Thai', 'Vietnamese', 'German', 'French', 'Spanish',
        'Italian', 'Portuguese', 'Dutch', 'Polish', 'Turkish', 'Greek',
        'Hebrew', 'Indonesian', 'Malay', 'Filipino', 'Persian', 'Bengali',
        'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Gujarati', 'Punjabi',
        # ... and 79 more
    ]
    
    def __init__(self):
        """
        Initialize PaddleOCR-VL with CPU-only mode
        
        Note: VL model is resource-intensive (~2GB memory)
        """
        self._pipeline = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the PaddleOCR-VL pipeline"""
        try:
            self._pipeline = PaddleOCRVL(
                device='cpu',  # Force CPU-only mode
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PaddleOCR-VL: {e}")
    
    def parse_document(self, image, output_dir=None):
        """
        Parse document using Vision-Language model
        
        Args:
            image: Image path, URL, or numpy array
            output_dir: Optional directory for saving outputs
            
        Returns:
            dict with parsed results including text, structure, and exports
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        result = self._pipeline.predict(image)
        
        parsed_result = {
            'elements': [],
            'markdown': '',
            'json_data': None,
            'full_text': '',
        }
        
        for res in result:
            # Extract elements
            if hasattr(res, 'elements') and res.elements:
                for elem in res.elements:
                    element = {
                        'type': elem.type if hasattr(elem, 'type') else 'text',
                        'content': elem.content if hasattr(elem, 'content') else '',
                        'box': elem.box.tolist() if hasattr(elem, 'box') and elem.box is not None else None,
                    }
                    parsed_result['elements'].append(element)
            
            # Extract text content
            if hasattr(res, 'text') and res.text:
                parsed_result['full_text'] = res.text
            
            # Try to save markdown
            try:
                res.save_to_markdown(save_path=output_dir)
                md_files = [f for f in os.listdir(output_dir) if f.endswith('.md')]
                if md_files:
                    with open(os.path.join(output_dir, md_files[0]), 'r', encoding='utf-8') as f:
                        parsed_result['markdown'] = f.read()
            except Exception:
                pass
            
            # Try to save JSON
            try:
                res.save_to_json(save_path=output_dir)
                json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
                if json_files:
                    with open(os.path.join(output_dir, json_files[0]), 'r', encoding='utf-8') as f:
                        parsed_result['json_data'] = json.load(f)
            except Exception:
                pass
        
        return parsed_result
    
    def get_supported_languages(self):
        """Return list of supported languages"""
        return self.SUPPORTED_LANGUAGES
    
    def is_available(self):
        """Check if VL model is available and loaded"""
        return self._pipeline is not None
