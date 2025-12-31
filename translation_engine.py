"""
Document Translation Engine (PP-DocTranslation)
Translate documents from one language to another while preserving layout
"""
import os
import tempfile
import json
from typing import Dict, List, Optional, Any


class TranslationEngine:
    """Wrapper around PP-DocTranslation for document translation"""

    # Supported language pairs
    SUPPORTED_LANGUAGES = {
        'zh': 'Chinese',
        'en': 'English',
        'ja': 'Japanese',
        'ko': 'Korean',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'th': 'Thai',
        'vi': 'Vietnamese',
    }

    def __init__(self, api_key: str = None, source_lang: str = 'en',
                 target_lang: str = 'zh'):
        """
        Initialize PP-DocTranslation with ERNIE 4.5

        Args:
            api_key: API key for ERNIE/Qianfan
            source_lang: Source language code
            target_lang: Target language code
        """
        self.api_key = api_key
        self.source_lang = source_lang
        self.target_lang = target_lang
        self._pipeline = None

    def _initialize(self):
        """Initialize the PP-DocTranslation pipeline"""
        try:
            from paddleocr import PPDocTranslation
            
            self._pipeline = PPDocTranslation(
                device='cpu',
            )
        except ImportError:
            raise RuntimeError("PP-DocTranslation requires paddleocr[all]. Install with: pip install 'paddleocr[all]'")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PP-DocTranslation: {e}")

    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)

    def translate_document(self, input_path: str, output_dir: str = None,
                          source_lang: str = None, target_lang: str = None) -> Dict[str, Any]:
        """
        Translate a document (image, PDF, or Markdown)

        Args:
            input_path: Path to input document
            output_dir: Directory to save translated output
            source_lang: Source language (optional, uses default)
            target_lang: Target language (optional, uses default)

        Returns:
            dict with translation results and output paths
        """
        if not self.is_configured():
            return {
                'error': 'API key not configured',
                'message': 'Please configure your ERNIE API key in settings',
            }

        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        src = source_lang or self.source_lang
        tgt = target_lang or self.target_lang

        if self._pipeline is None:
            self._initialize()

        try:
            # Configure translation
            llm_config = {
                'module_name': 'chat_bot',
                'model_name': 'ernie-4.5-8k',
                'base_url': 'https://qianfan.baidubce.com/v2',
                'api_type': 'openai',
                'api_key': self.api_key,
            }

            # Perform translation
            result = self._pipeline.translate(
                input=input_path,
                source_lang=src,
                target_lang=tgt,
                save_path=output_dir,
                llm_config=llm_config,
            )

            # Collect output files
            output_files = []
            if os.path.exists(output_dir):
                for f in os.listdir(output_dir):
                    output_files.append(os.path.join(output_dir, f))

            # Read translated markdown if available
            translated_markdown = ''
            md_files = [f for f in output_files if f.endswith('.md')]
            if md_files:
                with open(md_files[0], 'r', encoding='utf-8') as f:
                    translated_markdown = f.read()

            return {
                'success': True,
                'source_lang': src,
                'target_lang': tgt,
                'output_dir': output_dir,
                'output_files': output_files,
                'translated_markdown': translated_markdown,
            }

        except Exception as e:
            return {
                'error': str(e),
                'source_lang': src,
                'target_lang': tgt,
            }

    def translate_text(self, text: str, source_lang: str = None,
                       target_lang: str = None) -> Dict[str, Any]:
        """
        Translate plain text using LLM

        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language

        Returns:
            dict with translated text
        """
        if not self.is_configured():
            return {
                'error': 'API key not configured',
            }

        src = source_lang or self.source_lang
        tgt = target_lang or self.target_lang

        try:
            import requests

            # Use ERNIE API for text translation
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }

            prompt = f"Translate the following text from {self.SUPPORTED_LANGUAGES.get(src, src)} to {self.SUPPORTED_LANGUAGES.get(tgt, tgt)}. Only output the translation, nothing else.\n\nText: {text}"

            response = requests.post(
                'https://qianfan.baidubce.com/v2/chat/completions',
                headers=headers,
                json={
                    'model': 'ernie-4.5-8k',
                    'messages': [{'role': 'user', 'content': prompt}],
                },
            )

            if response.status_code == 200:
                data = response.json()
                translated = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                return {
                    'success': True,
                    'original': text,
                    'translated': translated,
                    'source_lang': src,
                    'target_lang': tgt,
                }
            else:
                return {
                    'error': f'API error: {response.status_code}',
                    'original': text,
                }

        except Exception as e:
            return {
                'error': str(e),
                'original': text,
            }

    def get_supported_languages(self) -> Dict[str, str]:
        """Return supported languages"""
        return self.SUPPORTED_LANGUAGES

    def update_config(self, api_key: str = None, source_lang: str = None,
                      target_lang: str = None):
        """Update translation configuration"""
        if api_key is not None:
            self.api_key = api_key
        if source_lang is not None:
            self.source_lang = source_lang
        if target_lang is not None:
            self.target_lang = target_lang
