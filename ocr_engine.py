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
        'en': 'English',
        
        # Latin - European (PP-OCRv5 codes)
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'es': 'Spanish',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'pl': 'Polish',
        'ro': 'Romanian',
        'hu': 'Hungarian',
        'cs': 'Czech',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'hr': 'Croatian',
        'bs': 'Bosnian',
        'sq': 'Albanian',
        'da': 'Danish',
        'sv': 'Swedish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'et': 'Estonian',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'is': 'Icelandic',
        'ga': 'Irish',
        'cy': 'Welsh',
        'mt': 'Maltese',
        'la': 'Latin',
        'eu': 'Basque',
        'gl': 'Galician',
        'ca': 'Catalan',
        'oc': 'Occitan',
        'lb': 'Luxembourgish',
        'rm': 'Romansh',
        
        # Latin - Other
        'af': 'Afrikaans',
        'az': 'Azerbaijani',
        'id': 'Indonesian',
        'ms': 'Malay',
        'vi': 'Vietnamese',
        'tl': 'Tagalog/Filipino',
        'sw': 'Swahili',
        'tr': 'Turkish',
        'uz': 'Uzbek',
        'mi': 'Maori',
        'pi': 'Pali',
        'ku': 'Kurdish',
        'qu': 'Quechua',
        'rs_latin': 'Serbian (Latin)',
        
        # Cyrillic
        'ru': 'Russian',
        'uk': 'Ukrainian',
        'be': 'Belarusian',
        'bg': 'Bulgarian',
        'mk': 'Macedonian',
        'sr': 'Serbian (Cyrillic)',
        'rs_cyrillic': 'Serbian (Cyrillic)',
        'mn': 'Mongolian',
        'kk': 'Kazakh',
        'ky': 'Kyrgyz',
        'tg': 'Tajik',
        'tt': 'Tatar',
        'cv': 'Chuvash',
        'ba': 'Bashkir',
        'abq': 'Abaza',
        'ady': 'Adyghe',
        'kbd': 'Kabardian',
        'ava': 'Avaric',
        'dar': 'Dargwa',
        'inh': 'Ingush',
        'che': 'Chechen',
        'lbe': 'Lak',
        'lez': 'Lezgian',
        'tab': 'Tabasaran',
        'udm': 'Udmurt',
        'kv': 'Komi',
        'os': 'Ossetian',
        'bua': 'Buryat',
        'xal': 'Kalmyk',
        'tyv': 'Tuvan',
        'sah': 'Sakha/Yakut',
        'kaa': 'Karakalpak',
        'mns': 'Mansi',
        'mo': 'Moldovan',
        'ab': 'Abkhazian',
        
        # Arabic Script
        'ar': 'Arabic',
        'fa': 'Persian/Farsi',
        'ur': 'Urdu',
        'ug': 'Uyghur',
        'ps': 'Pashto',
        'sd': 'Sindhi',
        'bal': 'Balochi',
        
        # Indic Scripts (Devanagari)
        'hi': 'Hindi',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'bh': 'Bihari',
        'mai': 'Maithili',
        'ang': 'Angika',
        'bho': 'Bhojpuri',
        'mah': 'Magahi',
        'sck': 'Sadri',
        'new': 'Newari',
        'gom': 'Konkani',
        'sa': 'Sanskrit',
        'bgc': 'Haryanvi',
        
        # Other Indic Scripts
        'ta': 'Tamil',
        'te': 'Telugu',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'or': 'Odia/Oriya',
        'as': 'Assamese',
        
        # Southeast Asian
        'th': 'Thai',
        'ka': 'Georgian',
        'my': 'Myanmar/Burmese',
        'km': 'Khmer',
        'lo': 'Lao',
        'si': 'Sinhala',
        
        # Other
        'el': 'Greek',
        'he': 'Hebrew',
        'am': 'Amharic',
        'ti': 'Tigrinya',
        'hy': 'Armenian',
    }
    
    # Language groups for UI organization
    LANGUAGE_GROUPS = {
        'East Asian': ['ch', 'chinese_cht', 'japan', 'korean', 'en'],
        'Latin - European': [
            'fr', 'de', 'it', 'es', 'pt', 'nl', 'pl', 'ro', 'hu', 'cs', 'sk', 'sl',
            'hr', 'bs', 'sq', 'da', 'sv', 'no', 'fi', 'et', 'lv', 'lt', 'is', 'ga',
            'cy', 'mt', 'la', 'eu', 'gl', 'ca', 'oc', 'lb', 'rm'
        ],
        'Latin - Other': [
            'af', 'az', 'id', 'ms', 'vi', 'tl', 'sw', 'tr', 'uz', 'mi', 'pi', 'ku',
            'qu', 'rs_latin'
        ],
        'Cyrillic': [
            'ru', 'uk', 'be', 'bg', 'mk', 'sr', 'rs_cyrillic', 'mn', 'kk', 'ky', 'tg',
            'tt', 'cv', 'ba', 'abq', 'ady', 'kbd', 'ava', 'dar', 'inh', 'che', 'lbe',
            'lez', 'tab', 'udm', 'kv', 'os', 'bua', 'xal', 'tyv', 'sah', 'kaa', 'mns',
            'mo', 'ab'
        ],
        'Arabic Script': ['ar', 'fa', 'ur', 'ug', 'ps', 'sd', 'bal'],
        'Indic - Devanagari': [
            'hi', 'mr', 'ne', 'bh', 'mai', 'ang', 'bho', 'mah', 'sck', 'new', 'gom',
            'sa', 'bgc'
        ],
        'Indic - Other': ['ta', 'te', 'kn', 'ml', 'bn', 'gu', 'pa', 'or', 'as'],
        'Southeast Asian': ['th', 'ka', 'my', 'km', 'lo', 'si'],
        'Other Scripts': ['el', 'he', 'am', 'ti', 'hy'],
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

