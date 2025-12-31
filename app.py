"""
PaddleOCR UI - Flask Backend
Main application with API endpoints for OCR, model management, and image processing
"""
import os
import tempfile
import uuid
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ocr_engine import OCREngine
from model_manager import ModelManager
from image_processor import ImageProcessor
from structure_engine import StructureEngine
from vl_engine import VLEngine
from chat_ocr_engine import ChatOCREngine
from translation_engine import TranslationEngine
from batch_processor import BatchProcessor

# Initialize Flask app
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff', 'pdf'}

# Initialize components
ocr_engine = None
structure_engine = None
vl_engine = None
model_manager = ModelManager()
chat_ocr_engine = None
translation_engine = None
batch_processor = BatchProcessor()
image_processor = ImageProcessor()


def get_ocr_engine(lang='en', version='PP-OCRv5'):
    """Get or create OCR engine with specified configuration"""
    global ocr_engine
    if ocr_engine is None or ocr_engine.lang != lang or ocr_engine.ocr_version != version:
        ocr_engine = OCREngine(lang=lang, ocr_version=version)
    return ocr_engine


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_temp_file(filepath):
    """Safely cleanup a temporary file"""
    try:
        if filepath and isinstance(filepath, str) and os.path.exists(filepath):
            os.unlink(filepath)
    except Exception:
        pass  # Ignore cleanup errors


# ==================== Page Routes ====================

@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')


# ==================== OCR API Routes ====================

@app.route('/api/ocr', methods=['POST'])
def perform_ocr():
    """
    Perform OCR on an uploaded image

    Request body:
        - file: Image file (multipart/form-data)
        - or image: Base64 encoded image (JSON)
        - lang: Language code (default: 'en')
        - version: OCR version (default: 'PP-OCRv5')
        - brightness: Brightness factor (default: 1.0)
        - contrast: Contrast factor (default: 1.0)
        - saturation: Saturation factor (default: 1.0)
        - sharpness: Sharpness factor (default: 1.0)

    Returns:
        JSON with OCR results
    """
    temp_filepath = None
    try:
        # Get parameters
        lang = request.form.get('lang', request.json.get('lang', 'en') if request.is_json else 'en')
        version = request.form.get('version', request.json.get('version', 'PP-OCRv5') if request.is_json else 'PP-OCRv5')

        # Get preprocessing parameters
        brightness = float(request.form.get('brightness', 1.0))
        contrast = float(request.form.get('contrast', 1.0))
        saturation = float(request.form.get('saturation', 1.0))
        sharpness = float(request.form.get('sharpness', 1.0))

        # Get image
        image = None

        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400

            # Save temporarily
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            image = temp_filepath

        elif request.is_json and 'image' in request.json:
            # Base64 encoded image
            image = request.json['image']
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Load and preprocess image
        pil_image = image_processor.load_image(image)
        processed_image = image_processor.apply_adjustments(
            pil_image,
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            sharpness=sharpness
        )

        # Convert to numpy for OCR
        np_image = image_processor.to_numpy(processed_image)

        # Get OCR engine and perform recognition
        engine = get_ocr_engine(lang=lang, version=version)
        result = engine.detect_text(np_image)

        # Return processed image as base64 for display
        result['processed_image'] = image_processor.to_base64(processed_image, format='PNG')

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


@app.route('/api/preprocess', methods=['POST'])
def preprocess_image():
    """
    Apply preprocessing to an image without OCR

    Request body:
        - image: Base64 encoded image
        - brightness, contrast, saturation, sharpness: Float factors
        - rotation: Rotation degrees
        - flip_h, flip_v: Boolean flip flags
        - grayscale: Convert to grayscale
        - invert: Invert colors

    Returns:
        JSON with processed image as base64
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'JSON body required'}), 400

        data = request.json

        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400

        # Load image
        pil_image = image_processor.load_image(data['image'])

        # Apply adjustments
        processed = image_processor.apply_adjustments(
            pil_image,
            brightness=float(data.get('brightness', 1.0)),
            contrast=float(data.get('contrast', 1.0)),
            saturation=float(data.get('saturation', 1.0)),
            sharpness=float(data.get('sharpness', 1.0)),
            rotation=float(data.get('rotation', 0)),
            flip_h=bool(data.get('flip_h', False)),
            flip_v=bool(data.get('flip_v', False)),
            grayscale_mode=bool(data.get('grayscale', False)),
            invert_mode=bool(data.get('invert', False))
        )

        result_base64 = image_processor.to_base64(processed, format='PNG')

        return jsonify({
            'image': result_base64,
            'width': processed.width,
            'height': processed.height
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    engine = get_ocr_engine()
    return jsonify(engine.get_available_languages())


@app.route('/api/versions', methods=['GET'])
def get_versions():
    """Get list of available OCR versions"""
    engine = get_ocr_engine()
    return jsonify(engine.get_available_versions())



@app.route('/api/language-groups', methods=['GET'])
def get_language_groups():
    """Get languages organized by script/region groups for better UI display"""
    engine = get_ocr_engine()
    groups = engine.get_language_groups()
    languages = engine.get_available_languages()
    
    # Build organized structure with language names
    organized = {}
    for group_name, lang_codes in groups.items():
        organized[group_name] = [
            {'code': code, 'name': languages.get(code, code)}
            for code in lang_codes if code in languages
        ]
    
    return jsonify({
        'groups': organized,
        'all_languages': languages,
        'total_count': len(languages)
    })

@app.route('/api/structure', methods=['POST'])
def parse_document():
    """
    Parse document using PP-StructureV3

    Request body:
        - file: Image file (multipart/form-data)
        - or image: Base64 encoded image (JSON)
        - lang: Language code (default: 'ch')
        - use_table: Enable table recognition (default: true)
        - use_formula: Enable formula recognition (default: true)

    Returns:
        JSON with parsed results including layout, tables, formulas, etc.
    """
    temp_filepath = None
    try:
        lang = request.form.get('lang', 'ch')

        # Get image
        image = None

        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400

            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            image = temp_filepath

        elif request.is_json and 'image' in request.json:
            image = request.json['image']
            lang = request.json.get('lang', 'ch')
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Get structure engine and parse document
        engine = get_structure_engine(lang=lang)
        result = engine.parse_document(image)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


@app.route('/api/structure/layout', methods=['GET'])
def get_layout_colors():
    """Get layout element color mapping for visualization"""
    engine = get_structure_engine()
    return jsonify(engine.get_layout_colors())


# ==================== VL API Routes ====================

@app.route('/api/vl', methods=['POST'])
def parse_with_vl():
    """
    Parse document using PaddleOCR-VL

    Request body:
        - file: Image file (multipart/form-data)
        - or image: Base64 encoded image (JSON)

    Returns:
        JSON with VL parsing results
    """
    temp_filepath = None
    try:
        # Get image
        image = None

        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400

            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            image = temp_filepath

        elif request.is_json and 'image' in request.json:
            image = request.json['image']
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Get VL engine and parse document
        engine = get_vl_engine()
        result = engine.parse_document(image)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


@app.route('/api/vl/languages', methods=['GET'])
def get_vl_languages():
    """Get list of languages supported by VL model"""
    engine = get_vl_engine()
    return jsonify({'languages': engine.get_supported_languages()})


# ==================== Model Management Routes ====================

@app.route('/api/models', methods=['GET'])
def list_models():
    """Get list of all available models with installation status"""
    models = model_manager.get_model_list()
    disk_usage = model_manager.get_disk_usage()

    return jsonify({
        'models': models,
        'disk_usage_bytes': disk_usage,
        'disk_usage_mb': round(disk_usage / (1024 * 1024), 2)
    })


@app.route('/api/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """Get information about a specific model"""
    info = model_manager.get_model_info(model_id)
    if info is None:
        return jsonify({'error': 'Model not found'}), 404
    return jsonify(info)


@app.route('/api/models/<model_id>/download', methods=['POST'])
def download_model(model_id):
    """Download a model from the registry"""
    try:
        # Simple progress tracking
        progress = {'downloaded': 0, 'total': 0}

        def progress_callback(downloaded, total):
            progress['downloaded'] = downloaded
            progress['total'] = total

        path = model_manager.download_model(model_id, callback=progress_callback)

        return jsonify({
            'success': True,
            'model_id': model_id,
            'path': path,
            'message': f'Model {model_id} downloaded successfully'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/api/models/<model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete an installed model"""
    try:
        success = model_manager.delete_model(model_id)

        if success:
            return jsonify({
                'success': True,
                'model_id': model_id,
                'message': f'Model {model_id} deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete model'}), 500

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500



# ==================== ChatOCR API Routes ====================

def get_chat_ocr_engine(api_key=None, provider='ernie'):
    """Get or create ChatOCR engine"""
    global chat_ocr_engine
    if chat_ocr_engine is None:
        chat_ocr_engine = ChatOCREngine(api_key=api_key, provider=provider)
    elif api_key:
        chat_ocr_engine.update_config(api_key=api_key, provider=provider)
    return chat_ocr_engine


@app.route('/api/chatocr/extract', methods=['POST'])
def extract_info():
    """
    Extract key information from a document using LLM
    
    Request body:
        - file: Image file
        - keys: JSON array of keys to extract
        - api_key: LLM API key
        - provider: LLM provider (ernie, openai, ollama)
    """
    temp_filepath = None
    try:
        api_key = request.form.get('api_key', '')
        provider = request.form.get('provider', 'ernie')
        keys_json = request.form.get('keys', '[]')
        keys = json.loads(keys_json) if keys_json else []
        
        if not keys:
            return jsonify({'error': 'No extraction keys provided'}), 400
        
        image = None
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            image = temp_filepath
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        engine = get_chat_ocr_engine(api_key=api_key, provider=provider)
        result = engine.extract_info(image, keys)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


@app.route('/api/chatocr/templates', methods=['GET'])
def get_extraction_templates():
    """Get available extraction templates"""
    engine = get_chat_ocr_engine()
    return jsonify(engine.get_extraction_templates())


@app.route('/api/chatocr/providers', methods=['GET'])
def get_llm_providers():
    """Get supported LLM providers"""
    engine = get_chat_ocr_engine()
    return jsonify(engine.get_supported_providers())


@app.route('/api/chatocr/ask', methods=['POST'])
def ask_document():
    """Ask a question about a document"""
    temp_filepath = None
    try:
        api_key = request.form.get('api_key', '')
        question = request.form.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        image = None
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            image = temp_filepath
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        engine = get_chat_ocr_engine(api_key=api_key)
        result = engine.ask_question(image, question)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


# ==================== Translation API Routes ====================

def get_translation_engine(api_key=None):
    """Get or create translation engine"""
    global translation_engine
    if translation_engine is None:
        translation_engine = TranslationEngine(api_key=api_key)
    elif api_key:
        translation_engine.update_config(api_key=api_key)
    return translation_engine


@app.route('/api/translate/document', methods=['POST'])
def translate_document():
    """
    Translate a document
    
    Request body:
        - file: Document file (image, PDF, or markdown)
        - source_lang: Source language code
        - target_lang: Target language code
        - api_key: ERNIE API key
    """
    temp_filepath = None
    try:
        api_key = request.form.get('api_key', '')
        source_lang = request.form.get('source_lang', 'en')
        target_lang = request.form.get('target_lang', 'zh')
        
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
        else:
            return jsonify({'error': 'No file provided'}), 400
        
        engine = get_translation_engine(api_key=api_key)
        result = engine.translate_document(temp_filepath, source_lang=source_lang, target_lang=target_lang)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


@app.route('/api/translate/text', methods=['POST'])
def translate_text():
    """Translate plain text"""
    try:
        data = request.json
        api_key = data.get('api_key', '')
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'zh')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        engine = get_translation_engine(api_key=api_key)
        result = engine.translate_text(text, source_lang=source_lang, target_lang=target_lang)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/translate/languages', methods=['GET'])
def get_translation_languages():
    """Get supported translation languages"""
    engine = get_translation_engine()
    return jsonify(engine.get_supported_languages())


# ==================== Batch Processing API Routes ====================

@app.route('/api/batch/create', methods=['POST'])
def create_batch_job():
    """
    Create a batch processing job
    
    Request body:
        - files: Multiple files
        - job_type: 'ocr', 'structure', or 'vl'
        - options: JSON options
    """
    try:
        job_type = request.form.get('job_type', 'ocr')
        options_json = request.form.get('options', '{}')
        options = json.loads(options_json) if options_json else {}
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        # Save files temporarily
        file_paths = []
        for file in files:
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_paths.append(filepath)
        
        # Create batch job
        job_id = batch_processor.create_job(job_type, file_paths, options)
        
        return jsonify({
            'job_id': job_id,
            'job_type': job_type,
            'file_count': len(file_paths),
            'status': 'pending',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch/<job_id>/process', methods=['POST'])
def process_batch_job(job_id):
    """Start processing a batch job"""
    try:
        job = batch_processor.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        job_type = job['job_type']
        
        if job_type == 'ocr':
            lang = request.json.get('lang', 'en') if request.is_json else 'en'
            version = request.json.get('version', 'PP-OCRv5') if request.is_json else 'PP-OCRv5'
            engine = get_ocr_engine(lang=lang, version=version)
            result = batch_processor.process_ocr_batch(job_id, engine)
        elif job_type == 'structure':
            lang = request.json.get('lang', 'ch') if request.is_json else 'ch'
            engine = get_structure_engine(lang=lang)
            result = batch_processor.process_structure_batch(job_id, engine)
        elif job_type == 'vl':
            engine = get_vl_engine()
            result = batch_processor.process_vl_batch(job_id, engine)
        else:
            return jsonify({'error': f'Unknown job type: {job_type}'}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch/<job_id>', methods=['GET'])
def get_batch_job(job_id):
    """Get batch job status and results"""
    job = batch_processor.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/api/batch/<job_id>', methods=['DELETE'])
def delete_batch_job(job_id):
    """Delete a batch job"""
    if batch_processor.delete_job(job_id):
        return jsonify({'success': True, 'message': f'Job {job_id} deleted'})
    return jsonify({'error': 'Job not found'}), 404


@app.route('/api/batch/<job_id>/export', methods=['POST'])
def export_batch_results(job_id):
    """Export batch job results to files"""
    try:
        result = batch_processor.export_results(job_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch', methods=['GET'])
def list_batch_jobs():
    """List all batch jobs"""
    return jsonify(batch_processor.list_jobs())


# ==================== OCR with Character Coordinates ====================

@app.route('/api/ocr/chars', methods=['POST'])
def perform_ocr_with_chars():
    """
    Perform OCR with single-character coordinates
    
    Same as /api/ocr but returns character-level bounding boxes
    """
    temp_filepath = None
    try:
        lang = request.form.get('lang', 'en')
        version = request.form.get('version', 'PP-OCRv5')
        
        image = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type'}), 400
            
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_filepath)
            image = temp_filepath
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        engine = get_ocr_engine(lang=lang, version=version)
        result = engine.detect_text_with_chars(image)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cleanup_temp_file(temp_filepath)


# ==================== Static Files ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)


# ==================== Main Entry Point ====================

if __name__ == '__main__':
    print("=" * 50)
    print("PaddleOCR UI Server")
    print("=" * 50)
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Model directory: {model_manager.model_dir}")
    print("Starting server at http://localhost:5000")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)









