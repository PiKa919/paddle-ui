"""
PP-StructureV3 Engine Wrapper
Handles document parsing with layout detection, tables, formulas, charts, and seal text
Supports both images and PDF files
"""
import os
import tempfile
import json
from paddleocr import PPStructureV3
import numpy as np


class StructureEngine:
    """Wrapper around PP-StructureV3 for document parsing"""

    # Layout element types
    LAYOUT_TYPES = {
        'text': {'color': '#6366f1', 'label': 'Text'},
        'title': {'color': '#f59e0b', 'label': 'Title'},
        'figure': {'color': '#10b981', 'label': 'Figure'},
        'table': {'color': '#ef4444', 'label': 'Table'},
        'formula': {'color': '#8b5cf6', 'label': 'Formula'},
        'list': {'color': '#06b6d4', 'label': 'List'},
        'header': {'color': '#ec4899', 'label': 'Header'},
        'footer': {'color': '#84cc16', 'label': 'Footer'},
        'seal': {'color': '#f97316', 'label': 'Seal'},
        'chart': {'color': '#14b8a6', 'label': 'Chart'},
    }

    # Supported file types
    SUPPORTED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff', 'pdf'}

    def __init__(self, lang='ch', use_table=True, use_formula=True,
                 use_chart=True, use_seal=True):
        """
        Initialize PP-StructureV3 with CPU-only mode

        Args:
            lang: Language code (default: 'ch' for Chinese+English)
            use_table: Enable table recognition
            use_formula: Enable formula recognition
            use_chart: Enable chart parsing
            use_seal: Enable seal text recognition
        """
        self.lang = lang
        self.use_table = use_table
        self.use_formula = use_formula
        self.use_chart = use_chart
        self.use_seal = use_seal
        self._pipeline = None
        self._initialize()

    def _initialize(self):
        """Initialize the PP-StructureV3 pipeline"""
        try:
            self._pipeline = PPStructureV3(
                lang=self.lang,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_table_recognition=self.use_table,
                use_formula_recognition=self.use_formula,
                use_chart_parsing=self.use_chart,
                use_seal_recognition=self.use_seal,
                device='cpu',  # Force CPU-only mode
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PP-StructureV3: {e}")

    def is_pdf(self, file_path):
        """Check if file is a PDF"""
        if isinstance(file_path, str):
            return file_path.lower().endswith('.pdf')
        return False

    def parse_document(self, image, output_dir=None):
        """
        Parse document and extract structured content.
        Supports both images and PDF files.

        Args:
            image: Image path, PDF path, URL, or numpy array
            output_dir: Optional directory for saving outputs

        Returns:
            dict with parsed results including layout, tables, formulas, etc.
            For PDFs, includes 'pages' with per-page results.
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        # Check if this is a PDF
        is_pdf_file = self.is_pdf(image)
        
        result = self._pipeline.predict(image)

        if is_pdf_file:
            return self._parse_pdf_result(result, output_dir)
        else:
            return self._parse_image_result(result, output_dir)

    def _parse_image_result(self, result, output_dir):
        """Parse result from single image"""
        parsed_result = {
            'layout': [],
            'tables': [],
            'formulas': [],
            'charts': [],
            'seals': [],
            'text_blocks': [],
            'markdown': '',
            'json_data': None,
            'page_count': 1,
        }

        for res in result:
            self._extract_elements(res, parsed_result, output_dir)

        return parsed_result

    def _parse_pdf_result(self, result, output_dir):
        """Parse result from multi-page PDF"""
        pages = []
        combined_markdown = []
        all_tables = []
        all_formulas = []
        
        for page_idx, res in enumerate(result):
            page_result = {
                'page': page_idx + 1,
                'layout': [],
                'tables': [],
                'formulas': [],
                'charts': [],
                'seals': [],
                'text_blocks': [],
                'markdown': '',
            }
            
            self._extract_elements(res, page_result, output_dir)
            pages.append(page_result)
            
            if page_result['markdown']:
                combined_markdown.append(f"## Page {page_idx + 1}\n\n{page_result['markdown']}")
            all_tables.extend(page_result['tables'])
            all_formulas.extend(page_result['formulas'])

        return {
            'pages': pages,
            'page_count': len(pages),
            'tables': all_tables,
            'formulas': all_formulas,
            'markdown': '\n\n---\n\n'.join(combined_markdown),
            'json_data': {'pages': pages},
        }

    def _extract_elements(self, res, parsed_result, output_dir):
        """Extract all elements from a single result object"""
        # Extract layout information
        if hasattr(res, 'layout_parsing_result') and res.layout_parsing_result:
            layout_result = res.layout_parsing_result

            if hasattr(layout_result, 'boxes') and layout_result.boxes is not None:
                for i, box in enumerate(layout_result.boxes):
                    box_coords = box.tolist() if isinstance(box, np.ndarray) else box
                    label = layout_result.labels[i] if hasattr(layout_result, 'labels') else 'unknown'
                    score = layout_result.scores[i] if hasattr(layout_result, 'scores') else 1.0

                    element = {
                        'type': label.lower() if isinstance(label, str) else 'unknown',
                        'box': box_coords,
                        'confidence': float(score) if score else 1.0,
                    }
                    parsed_result['layout'].append(element)

        # Extract tables
        if hasattr(res, 'table_res_list') and res.table_res_list:
            for table_res in res.table_res_list:
                if hasattr(table_res, 'html') and table_res.html:
                    parsed_result['tables'].append({
                        'html': table_res.html,
                        'box': table_res.box.tolist() if hasattr(table_res, 'box') and table_res.box is not None else None,
                    })

        # Extract formulas
        if hasattr(res, 'formula_res_list') and res.formula_res_list:
            for formula_res in res.formula_res_list:
                if hasattr(formula_res, 'latex') and formula_res.latex:
                    parsed_result['formulas'].append({
                        'latex': formula_res.latex,
                        'box': formula_res.box.tolist() if hasattr(formula_res, 'box') and formula_res.box is not None else None,
                    })

        # Extract chart info
        if hasattr(res, 'chart_res_list') and res.chart_res_list:
            for chart_res in res.chart_res_list:
                parsed_result['charts'].append({
                    'data': chart_res.data if hasattr(chart_res, 'data') else None,
                    'box': chart_res.box.tolist() if hasattr(chart_res, 'box') and chart_res.box is not None else None,
                })

        # Extract seal text
        if hasattr(res, 'seal_res_list') and res.seal_res_list:
            for seal_res in res.seal_res_list:
                if hasattr(seal_res, 'text') and seal_res.text:
                    parsed_result['seals'].append({
                        'text': seal_res.text,
                        'box': seal_res.box.tolist() if hasattr(seal_res, 'box') and seal_res.box is not None else None,
                    })

        # Extract text blocks
        if hasattr(res, 'text_res_list') and res.text_res_list:
            for text_res in res.text_res_list:
                if hasattr(text_res, 'text') and text_res.text:
                    parsed_result['text_blocks'].append({
                        'text': text_res.text,
                        'box': text_res.box.tolist() if hasattr(text_res, 'box') and text_res.box is not None else None,
                    })

        # Try to save/get markdown
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

    def get_layout_colors(self):
        """Return layout type color mapping for visualization"""
        return self.LAYOUT_TYPES

    def get_supported_extensions(self):
        """Return supported file extensions"""
        return self.SUPPORTED_EXTENSIONS

    def detect_layout_only(self, image):
        """
        Detect layout without full parsing (faster)

        Args:
            image: Image path, URL, or numpy array

        Returns:
            dict with layout elements only
        """
        result = self.parse_document(image)
        return {
            'layout': result.get('layout', []),
            'colors': self.LAYOUT_TYPES,
        }
