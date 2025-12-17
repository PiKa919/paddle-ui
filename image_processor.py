"""
Image Processor for PaddleOCR UI
Handles image preprocessing: brightness, contrast, saturation, etc.
"""
import numpy as np
from PIL import Image, ImageEnhance
import io
import base64


class ImageProcessor:
    """Image preprocessing utilities for OCR"""
    
    @staticmethod
    def load_image(image_source):
        """
        Load image from various sources
        
        Args:
            image_source: File path, bytes, or base64 string
            
        Returns:
            PIL Image object
        """
        if isinstance(image_source, str):
            if image_source.startswith('data:image'):
                # Base64 data URL
                header, data = image_source.split(',', 1)
                image_bytes = base64.b64decode(data)
                return Image.open(io.BytesIO(image_bytes))
            else:
                # File path
                return Image.open(image_source)
        elif isinstance(image_source, bytes):
            return Image.open(io.BytesIO(image_source))
        elif isinstance(image_source, Image.Image):
            return image_source
        else:
            raise ValueError(f"Unsupported image source type: {type(image_source)}")
    
    @staticmethod
    def to_base64(image, format='PNG'):
        """Convert PIL Image to base64 data URL"""
        buffered = io.BytesIO()
        
        # Convert RGBA to RGB if saving as JPEG
        if format.upper() == 'JPEG' and image.mode == 'RGBA':
            image = image.convert('RGB')
        
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        mime_type = f"image/{format.lower()}"
        return f"data:{mime_type};base64,{img_str}"
    
    @staticmethod
    def to_numpy(image):
        """Convert PIL Image to numpy array for PaddleOCR"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return np.array(image)
    
    @staticmethod
    def adjust_brightness(image, factor):
        """
        Adjust image brightness
        
        Args:
            image: PIL Image
            factor: Brightness factor (1.0 = original, <1 darker, >1 brighter)
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_contrast(image, factor):
        """
        Adjust image contrast
        
        Args:
            image: PIL Image
            factor: Contrast factor (1.0 = original, <1 less contrast, >1 more contrast)
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_saturation(image, factor):
        """
        Adjust image saturation
        
        Args:
            image: PIL Image
            factor: Saturation factor (1.0 = original, 0 = grayscale, >1 more saturated)
        """
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def adjust_sharpness(image, factor):
        """
        Adjust image sharpness
        
        Args:
            image: PIL Image
            factor: Sharpness factor (1.0 = original, <1 blur, >1 sharpen)
        """
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def rotate(image, degrees):
        """Rotate image by specified degrees"""
        return image.rotate(-degrees, expand=True, fillcolor='white')
    
    @staticmethod
    def flip_horizontal(image):
        """Flip image horizontally"""
        from PIL import ImageOps
        return ImageOps.mirror(image)
    
    @staticmethod
    def flip_vertical(image):
        """Flip image vertically"""
        from PIL import ImageOps
        return ImageOps.flip(image)
    
    @staticmethod
    def grayscale(image):
        """Convert image to grayscale"""
        return image.convert('L').convert('RGB')
    
    @staticmethod
    def invert(image):
        """Invert image colors"""
        from PIL import ImageOps
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb = Image.merge('RGB', (r, g, b))
            inverted = ImageOps.invert(rgb)
            r, g, b = inverted.split()
            return Image.merge('RGBA', (r, g, b, a))
        elif image.mode == 'RGB':
            return ImageOps.invert(image)
        else:
            return ImageOps.invert(image.convert('RGB'))
    
    @classmethod
    def apply_adjustments(cls, image, brightness=1.0, contrast=1.0, 
                         saturation=1.0, sharpness=1.0, rotation=0,
                         flip_h=False, flip_v=False, grayscale_mode=False,
                         invert_mode=False):
        """
        Apply multiple adjustments to an image
        
        Args:
            image: PIL Image or image source
            brightness: Brightness factor
            contrast: Contrast factor
            saturation: Saturation factor
            sharpness: Sharpness factor
            rotation: Rotation degrees
            flip_h: Flip horizontally
            flip_v: Flip vertically
            grayscale_mode: Convert to grayscale
            invert_mode: Invert colors
            
        Returns:
            Processed PIL Image
        """
        if not isinstance(image, Image.Image):
            image = cls.load_image(image)
        
        # Apply adjustments in order
        if brightness != 1.0:
            image = cls.adjust_brightness(image, brightness)
        
        if contrast != 1.0:
            image = cls.adjust_contrast(image, contrast)
        
        if saturation != 1.0:
            image = cls.adjust_saturation(image, saturation)
        
        if sharpness != 1.0:
            image = cls.adjust_sharpness(image, sharpness)
        
        if rotation != 0:
            image = cls.rotate(image, rotation)
        
        if flip_h:
            image = cls.flip_horizontal(image)
        
        if flip_v:
            image = cls.flip_vertical(image)
        
        if grayscale_mode:
            image = cls.grayscale(image)
        
        if invert_mode:
            image = cls.invert(image)
        
        return image
