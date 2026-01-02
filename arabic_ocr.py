"""
Standalone Arabic OCR Script (Recognition Only)
===============================================

This script performs Arabic text recognition on images using PaddleOCR models.
It is designed to work in "Recognition Only" mode, meaning it expects images
that already contain cropped text lines (no text detection is performed).

-------------------------------------------------------------------------------
PREREQUISITES & INSTALLATION
-------------------------------------------------------------------------------

1. Install Python 3.8+

2. Install PaddlePaddle (CPU version):
   pip install paddlepaddle

   # For GPU version (requires CUDA), check:
   # https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/en/install/pip/linux-pip_en.html

3. Install PaddleOCR and PaddleX:
   pip install paddleocr paddlex
   pip install pillow numpy

-------------------------------------------------------------------------------
MODELS
-------------------------------------------------------------------------------

This script uses the following official PaddleOCR Arabic recognition models:

1. PP-OCRv5 (Default, Recommended):
   - Model Name: arabic_PP-OCRv5_mobile_rec
   - Download: https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/arabic_PP-OCRv5_mobile_rec_infer.tar
   
2. PP-OCRv3 (Legacy):
   - Model Name: arabic_PP-OCRv3_mobile_rec
   - Download: https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/arabic_PP-OCRv3_mobile_rec_infer.tar

Note: The script attempts to download models automatically using PaddleX.
If automatic download fails, you can manually download the .tar files, extract them,
and place them in `~/.paddlex/official_models/`.

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------

Command Line:
    python arabic_ocr.py <image_path> [version]

    Examples:
    python arabic_ocr.py cropped_text.jpg             # Uses PP-OCRv5
    python arabic_ocr.py cropped_text.jpg PP-OCRv3    # Uses PP-OCRv3

Python Module:
    from arabic_ocr import ArabicOCR
    
    ocr = ArabicOCR()
    result = ocr.predict('path/to/image.jpg')
    print(result['text'], result['confidence'])

-------------------------------------------------------------------------------
"""

import os
import sys

# Suppress PaddlePaddle warnings and checks
os.environ['DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['FLAGS_minloglevel'] = '2'

try:
    from PIL import Image
    import numpy as np
    from paddlex import create_model
except ImportError as e:
    print("\nError: Missing dependencies.")
    print(f"Details: {e}")
    print("\nPlease install required packages:")
    print("pip install paddlepaddle paddleocr paddlex pillow numpy\n")
    sys.exit(1)


class ArabicOCR:
    """
    Arabic text recognition engine (No Text Detection).
    Optimized for recognizing text in pre-cropped images.
    """
    
    MODELS = {
        'PP-OCRv5': 'arabic_PP-OCRv5_mobile_rec',
        'PP-OCRv3': 'arabic_PP-OCRv3_mobile_rec',
    }
    
    def __init__(self, version='PP-OCRv5'):
        """
        Initialize the Arabic recognition model.
        
        Args:
            version (str): 'PP-OCRv5' (default) or 'PP-OCRv3'
        """
        if version not in self.MODELS:
            raise ValueError(f"Version must be one of: {list(self.MODELS.keys())}")
        
        self.version = version
        print(f"Loading Arabic OCR model: {self.version} ({self.MODELS[version]})...")
        
        try:
            # Load recognition-only model via PaddleX
            self._model = create_model(
                model_name=self.MODELS[version], 
                device='cpu' # Force CPU for compatibility
            )
        except Exception as e:
            print(f"Failed to load model: {e}")
            print("Ensure you have internet connection for first-time model download.")
            raise

    def predict(self, image):
        """
        Recognize Arabic text in an image.
        
        Args:
            image: File path (str), PIL Image object, or numpy array (RGB)
            
        Returns:
            dict: {'text': str, 'confidence': float}
        """
        # Handle different input types
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image not found: {image}")
            img = Image.open(image)
        elif isinstance(image, Image.Image):
            img = image
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image)
        else:
            raise ValueError("Unsupported image type. Use path, PIL Image, or numpy array.")
        
        # Ensure RGB format (PaddleOCR expects 3 channels)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array for inference
        img_np = np.array(img, dtype=np.uint8)
        
        # Run prediction
        # PaddleX returns a generator or list of results
        results = self._model.predict(img_np)
        
        # Process result (we expect one result for recognition-only)
        for res in results:
            text = res.get('rec_text', '')
            score = res.get('rec_score', 0.0)
            
            return {
                'text': text,
                'confidence': float(score)
            }
            
        # Fallback if no result yielded
        return {'text': '', 'confidence': 0.0}


if __name__ == "__main__":
    # Command line interface
    if len(sys.argv) < 2:
        print(__doc__) # Print the docstring at the top of the file
        sys.exit(1)
    
    image_path = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else 'PP-OCRv5'
    
    print("-" * 50)
    print(f"Processing: {image_path}")
    
    try:
        ocr = ArabicOCR(version=version)
        result = ocr.predict(image_path)
        
        print("-" * 50)
        print(f"Recognized Text : {result['text']}")
        print(f"Confidence      : {result['confidence']:.2%}")
        print("-" * 50)
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
