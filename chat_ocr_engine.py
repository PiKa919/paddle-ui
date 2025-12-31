"""
PP-ChatOCRv4 Engine Wrapper
LLM-based key information extraction from documents
Supports ERNIE 4.5 and other OpenAI-compatible LLM APIs
"""
import os
import tempfile
import json
from typing import List, Dict, Optional, Any


class ChatOCREngine:
    """Wrapper around PP-ChatOCRv4 for intelligent document understanding"""

    # Supported LLM providers
    SUPPORTED_PROVIDERS = {
        'ernie': {
            'name': 'ERNIE (Baidu)',
            'base_url': 'https://qianfan.baidubce.com/v2',
            'api_type': 'openai',
            'models': ['ernie-3.5-8k', 'ernie-4.0-8k', 'ernie-4.5-8k'],
        },
        'openai': {
            'name': 'OpenAI',
            'base_url': 'https://api.openai.com/v1',
            'api_type': 'openai',
            'models': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
        },
        'ollama': {
            'name': 'Ollama (Local)',
            'base_url': 'http://localhost:11434/v1',
            'api_type': 'openai',
            'models': ['llama3', 'mistral', 'qwen2'],
        },
        'custom': {
            'name': 'Custom OpenAI-compatible',
            'base_url': '',
            'api_type': 'openai',
            'models': [],
        },
    }

    # Common extraction templates
    EXTRACTION_TEMPLATES = {
        'invoice': {
            'name': 'Invoice',
            'keys': ['invoice_number', 'date', 'vendor', 'total_amount', 'tax', 'line_items'],
            'description': 'Extract key information from invoices',
        },
        'receipt': {
            'name': 'Receipt',
            'keys': ['store_name', 'date', 'items', 'subtotal', 'tax', 'total'],
            'description': 'Extract information from receipts',
        },
        'id_card': {
            'name': 'ID Card',
            'keys': ['name', 'id_number', 'date_of_birth', 'address', 'issue_date', 'expiry_date'],
            'description': 'Extract information from ID cards',
        },
        'business_card': {
            'name': 'Business Card',
            'keys': ['name', 'title', 'company', 'phone', 'email', 'address', 'website'],
            'description': 'Extract contact information from business cards',
        },
        'contract': {
            'name': 'Contract',
            'keys': ['parties', 'effective_date', 'terms', 'payment_terms', 'signatures'],
            'description': 'Extract key terms from contracts',
        },
        'custom': {
            'name': 'Custom',
            'keys': [],
            'description': 'Define your own extraction keys',
        },
    }

    def __init__(self, api_key: str = None, provider: str = 'ernie',
                 model_name: str = None, base_url: str = None):
        """
        Initialize PP-ChatOCRv4 with LLM configuration

        Args:
            api_key: API key for the LLM provider
            provider: LLM provider ('ernie', 'openai', 'ollama', 'custom')
            model_name: Model name to use
            base_url: Custom base URL (for 'custom' provider)
        """
        self.api_key = api_key
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self._pipeline = None
        self._visual_info = None
        self._vector_info = None
        
        # Validate provider
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

    def _get_config(self) -> Dict:
        """Build configuration for the LLM"""
        provider_config = self.SUPPORTED_PROVIDERS[self.provider]
        
        base_url = self.base_url or provider_config['base_url']
        model_name = self.model_name or (provider_config['models'][0] if provider_config['models'] else 'gpt-3.5-turbo')
        
        return {
            'module_name': 'chat_bot',
            'model_name': model_name,
            'base_url': base_url,
            'api_type': provider_config['api_type'],
            'api_key': self.api_key or 'dummy_key',
        }

    def _get_retriever_config(self) -> Dict:
        """Build configuration for the retriever (embedding model)"""
        return {
            'module_name': 'retriever',
            'model_name': 'embedding-v1',
            'base_url': self.SUPPORTED_PROVIDERS['ernie']['base_url'],
            'api_type': 'qianfan',
            'api_key': self.api_key or 'dummy_key',
        }

    def _initialize(self):
        """Initialize the PP-ChatOCRv4 pipeline"""
        try:
            from paddleocr import PPChatOCRv4Doc
            
            self._pipeline = PPChatOCRv4Doc(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                device='cpu',
            )
        except ImportError:
            raise RuntimeError("PP-ChatOCRv4 requires paddleocr[all]. Install with: pip install 'paddleocr[all]'")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PP-ChatOCRv4: {e}")

    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)

    def extract_info(self, image: str, keys: List[str], 
                     use_ocr: bool = True, use_table: bool = True,
                     use_seal: bool = True, use_mllm: bool = False) -> Dict[str, Any]:
        """
        Extract key information from a document

        Args:
            image: Image path, URL, or base64 string
            keys: List of information keys to extract (e.g., ['name', 'date', 'amount'])
            use_ocr: Use OCR for text extraction
            use_table: Use table recognition
            use_seal: Use seal recognition
            use_mllm: Use multimodal LLM (requires local mllm service)

        Returns:
            dict with extracted information and confidence scores
        """
        if not self.is_configured():
            return {
                'error': 'API key not configured',
                'message': 'Please configure your LLM API key in settings',
                'extracted': {},
            }

        if self._pipeline is None:
            self._initialize()

        try:
            # Step 1: Visual prediction (OCR + layout analysis)
            visual_result = self._pipeline.visual_predict(
                input=image,
                use_common_ocr=use_ocr,
                use_seal_recognition=use_seal,
                use_table_recognition=use_table,
            )

            # Extract visual info
            visual_info_list = []
            for res in visual_result:
                visual_info_list.append(res.get('visual_info', {}))
                self._visual_info = res.get('visual_info')

            # Step 2: Build vector index for retrieval
            retriever_config = self._get_retriever_config()
            vector_info = self._pipeline.build_vector(
                visual_info_list,
                flag_save_bytes_vector=True,
                retriever_config=retriever_config,
            )
            self._vector_info = vector_info

            # Step 3: Chat with LLM to extract information
            chat_config = self._get_config()
            chat_result = self._pipeline.chat(
                key_list=keys,
                visual_info=visual_info_list,
                vector_info=vector_info,
                mllm_predict_info=None,
                chat_bot_config=chat_config,
                retriever_config=retriever_config,
            )

            # Parse results
            extracted = {}
            for key in keys:
                if key in chat_result:
                    extracted[key] = {
                        'value': chat_result[key],
                        'confidence': chat_result.get(f'{key}_confidence', 1.0),
                    }
                else:
                    extracted[key] = {
                        'value': None,
                        'confidence': 0.0,
                    }

            return {
                'success': True,
                'extracted': extracted,
                'raw_response': chat_result,
                'keys_requested': keys,
            }

        except Exception as e:
            return {
                'error': str(e),
                'extracted': {},
                'keys_requested': keys,
            }

    def extract_with_template(self, image: str, template: str) -> Dict[str, Any]:
        """
        Extract information using a predefined template

        Args:
            image: Image path or URL
            template: Template name ('invoice', 'receipt', 'id_card', etc.)

        Returns:
            dict with extracted information
        """
        if template not in self.EXTRACTION_TEMPLATES:
            return {
                'error': f'Unknown template: {template}',
                'available_templates': list(self.EXTRACTION_TEMPLATES.keys()),
            }

        template_config = self.EXTRACTION_TEMPLATES[template]
        return self.extract_info(image, template_config['keys'])

    def ask_question(self, image: str, question: str) -> Dict[str, Any]:
        """
        Ask a natural language question about a document

        Args:
            image: Image path or URL
            question: Natural language question

        Returns:
            dict with answer and supporting context
        """
        if not self.is_configured():
            return {
                'error': 'API key not configured',
                'answer': None,
            }

        if self._pipeline is None:
            self._initialize()

        try:
            # Use the question as a key for extraction
            result = self.extract_info(image, [question])
            
            return {
                'success': True,
                'question': question,
                'answer': result.get('extracted', {}).get(question, {}).get('value'),
                'raw_response': result.get('raw_response'),
            }

        except Exception as e:
            return {
                'error': str(e),
                'question': question,
                'answer': None,
            }

    def get_supported_providers(self) -> Dict:
        """Return list of supported LLM providers"""
        return self.SUPPORTED_PROVIDERS

    def get_extraction_templates(self) -> Dict:
        """Return available extraction templates"""
        return self.EXTRACTION_TEMPLATES

    def update_config(self, api_key: str = None, provider: str = None,
                      model_name: str = None, base_url: str = None):
        """Update LLM configuration"""
        if api_key is not None:
            self.api_key = api_key
        if provider is not None:
            if provider not in self.SUPPORTED_PROVIDERS:
                raise ValueError(f"Unsupported provider: {provider}")
            self.provider = provider
        if model_name is not None:
            self.model_name = model_name
        if base_url is not None:
            self.base_url = base_url
        
        # Reset pipeline to use new config
        self._pipeline = None
