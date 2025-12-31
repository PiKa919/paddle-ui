"""
PaddleOCR Engine Wrapper
Handles OCR operations with CPU-only mode support
Updated for PaddleOCR 3.x with 109+ languages support
"""
import os
from paddleocr import PaddleOCR
import numpy as np


class OCREngine:
    """Wrapper around PaddleOCR for CPU-only inference"""

    # Complete language list from PaddleOCR 3.x (109 languages)
    # Grouped by script/region for better organization
    LANGUAGES = {
        # East Asian
        'ch': 'Chinese (Simplified)',
        'chinese_cht': 'Chinese (Traditional)',
        'japan': 'Japanese',
        'korean': 'Korean',
        
        # Latin Script - Major European Languages
        'en': 'English',
        'german': 'German',
        'french': 'French',
        'spanish': 'Spanish',
        'italian': 'Italian',
        'portuguese': 'Portuguese',
        'dutch': 'Dutch',
        'polish': 'Polish',
        'romanian': 'Romanian',
        'swedish': 'Swedish',
        'norwegian': 'Norwegian',
        'danish': 'Danish',
        'finnish': 'Finnish',
        'czech': 'Czech',
        'hungarian': 'Hungarian',
        'croatian': 'Croatian',
        'slovenian': 'Slovenian',
        'slovak': 'Slovak',
        'serbian_latin': 'Serbian (Latin)',
        'bosnian': 'Bosnian',
        'albanian': 'Albanian',
        'estonian': 'Estonian',
        'latvian': 'Latvian',
        'lithuanian': 'Lithuanian',
        'irish': 'Irish',
        'welsh': 'Welsh',
        'icelandic': 'Icelandic',
        'maltese': 'Maltese',
        'luxembourgish': 'Luxembourgish',
        'catalan': 'Catalan',
        'galician': 'Galician',
        'basque': 'Basque',
        
        # Latin Script - Other
        'latin': 'Latin (General)',
        'vietnamese': 'Vietnamese',
        'indonesian': 'Indonesian',
        'malay': 'Malay',
        'filipino': 'Filipino/Tagalog',
        'turkish': 'Turkish',
        'azerbaijani': 'Azerbaijani',
        'uzbek': 'Uzbek',
        'turkmen': 'Turkmen',
        'swahili': 'Swahili',
        'afrikaans': 'Afrikaans',
        'hausa': 'Hausa',
        'yoruba': 'Yoruba',
        'igbo': 'Igbo',
        'zulu': 'Zulu',
        'xhosa': 'Xhosa',
        'somali': 'Somali',
        
        # Cyrillic Script
        'cyrillic': 'Cyrillic (General)',
        'ru': 'Russian',
        'ukrainian': 'Ukrainian',
        'belarusian': 'Belarusian',
        'bulgarian': 'Bulgarian',
        'serbian_cyrillic': 'Serbian (Cyrillic)',
        'macedonian': 'Macedonian',
        'mongolian': 'Mongolian',
        'kazakh': 'Kazakh',
        'kyrgyz': 'Kyrgyz',
        'tajik': 'Tajik',
        
        # Arabic Script
        'ar': 'Arabic',
        'fa': 'Persian/Farsi',
        'ur': 'Urdu',
        'ps': 'Pashto',
        'ug': 'Uyghur',
        'ku': 'Kurdish',
        'sd': 'Sindhi',
        
        # Devanagari & Indic Scripts
        'devanagari': 'Devanagari (General)',
        'hi': 'Hindi',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'sa': 'Sanskrit',
        'bn': 'Bengali',
        'as': 'Assamese',
        'gu': 'Gujarati',
        'pa': 'Punjabi (Gurmukhi)',
        'or': 'Odia/Oriya',
        'ta': 'Tamil',
        'te': 'Telugu',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'si': 'Sinhala',
        
        # Southeast Asian Scripts
        'th': 'Thai',
        'lo': 'Lao',
        'my': 'Myanmar/Burmese',
        'km': 'Khmer',
        
        # Other Scripts
        'greek': 'Greek',
        'he': 'Hebrew',
        'am': 'Amharic',
        'ti': 'Tigrinya',
        'ka': 'Georgian',
        'hy': 'Armenian',
    }
    
    # Language groups for UI organization
    LANGUAGE_GROUPS = {
        'East Asian': ['ch', 'chinese_cht', 'japan', 'korean'],
        'Latin - European': ['en', 'german', 'french', 'spanish', 'italian', 'portuguese', 
                            'dutch', 'polish', 'romanian', 'swedish', 'norwegian', 'danish',
                            'finnish', 'czech', 'hungarian', 'croatian', 'slovenian', 'slovak',
                            'serbian_latin', 'bosnian', 'albanian', 'estonian', 'latvian',
                            'lithuanian', 'irish', 'welsh', 'icelandic', 'maltese',
                            'luxembourgish', 'catalan', 'galician', 'basque'],
        'Latin - Other': ['latin', 'vietnamese', 'indonesian', 'malay', 'filipino', 'turkish',
                         'azerbaijani', 'uzbek', 'turkmen', 'swahili', 'afrikaans', 'hausa',
                         'yoruba', 'igbo', 'zulu', 'xhosa', 'somali'],
        'Cyrillic': ['cyrillic', 'ru', 'ukrainian', 'belarusian', 'bulgarian', 'serbian_cyrillic',
                    'macedonian', 'mongolian', 'kazakh', 'kyrgyz', 'tajik'],
        'Arabic Script': ['ar', 'fa', 'ur', 'ps', 'ug', 'ku', 'sd'],
        'Indic Scripts': ['devanagari', 'hi', 'mr', 'ne', 'sa', 'bn', 'as', 'gu', 'pa', 'or',
                         'ta', 'te', 'kn', 'ml', 'si'],
        'Southeast Asian': ['th', 'lo', 'my', 'km'],
        'Other Scripts': ['greek', 'he', 'am', 'ti', 'ka', 'hy'],
    }

    # OCR versions available
    OCR_VERSIONS = ['PP-OCRv5', 'PP-OCRv4', 'PP-OCRv3']

    def __init__(self, lang='en', ocr_version='PP-OCRv5'):
        """
        Initialize PaddleOCR with CPU-only mode

        Args:
            lang: Language code (default: 'en')
            ocr_version: OCR model version (default: 'PP-OCRv5')

        Raises:
            ValueError: If lang or ocr_version is not supported
        """
        # Validate language
        if lang not in self.LANGUAGES:
            raise ValueError(f"Unsupported language: '{lang}'. Supported languages: {list(self.LANGUAGES.keys())}")
        
        # Validate OCR version
        if ocr_version not in self.OCR_VERSIONS:
            raise ValueError(f"Unsupported OCR version: '{ocr_version}'. Supported versions: {self.OCR_VERSIONS}")

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
        """
        Switch to a different model configuration

        Args:
            lang: New language code (optional)
            ocr_version: New OCR version (optional)

        Raises:
            ValueError: If lang or ocr_version is not supported
        """
        if lang is not None:
            if lang not in self.LANGUAGES:
                raise ValueError(f"Unsupported language: '{lang}'. Supported languages: {list(self.LANGUAGES.keys())}")
            self.lang = lang

        if ocr_version is not None:
            if ocr_version not in self.OCR_VERSIONS:
                raise ValueError(f"Unsupported OCR version: '{ocr_version}'. Supported versions: {self.OCR_VERSIONS}")
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


    def detect_text_with_chars(self, image):
        """
        Detect and recognize text with single-character coordinates.
        Available in PaddleOCR 3.2+

        Args:
            image: Image path, URL, or numpy array

        Returns:
            dict with 'boxes', 'texts', and 'char_coordinates' for each text box
        """
        result = self._ocr.predict(image)

        boxes = []
        texts = []

        for res in result:
            def get_value(obj, key, default=None):
                if isinstance(obj, dict) or hasattr(obj, 'keys'):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            rec_polys = get_value(res, 'rec_polys')
            rec_texts = get_value(res, 'rec_texts')
            rec_scores = get_value(res, 'rec_scores')
            # Character-level coordinates (PaddleOCR 3.2+)
            rec_char_polys = get_value(res, 'rec_char_polys')
            rec_char_scores = get_value(res, 'rec_char_scores')

            if rec_polys is not None and rec_texts is not None:
                scores = rec_scores if rec_scores is not None else [1.0] * len(rec_texts)
                char_polys_list = rec_char_polys if rec_char_polys is not None else [None] * len(rec_texts)
                char_scores_list = rec_char_scores if rec_char_scores is not None else [None] * len(rec_texts)
                
                for i, (poly, text, score) in enumerate(zip(rec_polys, rec_texts, scores)):
                    if poly is not None:
                        poly_list = poly.tolist() if isinstance(poly, np.ndarray) else poly
                        
                        # Process character coordinates
                        char_coords = []
                        if i < len(char_polys_list) and char_polys_list[i] is not None:
                            char_polys = char_polys_list[i]
                            char_scores = char_scores_list[i] if i < len(char_scores_list) and char_scores_list[i] is not None else [1.0] * len(text)
                            
                            for j, char in enumerate(text):
                                char_poly = char_polys[j] if j < len(char_polys) else None
                                char_score = char_scores[j] if j < len(char_scores) else 1.0
                                
                                if char_poly is not None:
                                    char_poly_list = char_poly.tolist() if isinstance(char_poly, np.ndarray) else char_poly
                                    char_coords.append({
                                        'char': char,
                                        'index': j,
                                        'points': char_poly_list,
                                        'confidence': float(char_score) if char_score else 1.0,
                                    })
                        
                        boxes.append({
                            'points': poly_list,
                            'text': text,
                            'confidence': float(score) if score else 1.0,
                            'char_coordinates': char_coords,
                        })
                        texts.append({
                            'text': text,
                            'confidence': float(score) if score else 1.0,
                            'char_count': len(text),
                            'has_char_coords': len(char_coords) > 0,
                        })

        return {
            'boxes': boxes,
            'texts': texts,
            'full_text': ' '.join([t['text'] for t in texts]),
            'char_level': True,
        }

    def get_available_languages(self):
        """Return dict of available languages"""
        return self.LANGUAGES

    def get_language_groups(self):
        """Return languages organized by script/region groups"""
        return self.LANGUAGE_GROUPS

    def get_available_versions(self):
        """Return list of available OCR versions"""
        return self.OCR_VERSIONS

