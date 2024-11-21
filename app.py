import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, send_from_directory, jsonify
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
import io
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import io
import os
import zipfile
from pdf2image import convert_from_bytes
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.debug = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File size too large'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error occurred'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error for debugging
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'sitemap.xml', mimetype='application/xml')

def allowed_file_size(files):
    MAX_FILE_SIZE = 4.5 * 1024 * 1024  # 4.5MB in bytes
    total_size = 0
    for file in files:
        total_size += len(file.read())
        file.seek(0)  # Reset file pointer
    return total_size <= MAX_FILE_SIZE

@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    try:
        if 'pdf_files' not in request.files:
            return jsonify({'error': 'No files selected'}), 400
        
        pdf_files = request.files.getlist('pdf_files')
        if not pdf_files or pdf_files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        if not allowed_file_size(pdf_files):
            return jsonify({'error': 'Total file size exceeds 4.5MB limit'}), 400

        merger = PdfMerger(strict=False)
        for pdf in pdf_files:
            if pdf and allowed_file(pdf.filename, ['pdf']):
                try:
                    pdf_stream = io.BytesIO(pdf.read())
                    merger.append(pdf_stream)
                except Exception as e:
                    return jsonify({'error': 'Invalid or corrupted PDF file'}), 400

        merged_pdf_stream = io.BytesIO()
        merger.write(merged_pdf_stream)
        merger.close()
        merged_pdf_stream.seek(0)

        return send_file(
            merged_pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
    except Exception as e:
        app.logger.error(f"Error in merge_pdfs: {str(e)}")
        return jsonify({'error': 'Failed to merge PDFs'}), 500

@app.route('/image_to_pdf', methods=['POST'])
def image_to_pdf():
    try:
        if 'image_files' not in request.files:
            return jsonify({'error': 'No files selected'}), 400
        
        image_files = request.files.getlist('image_files')
        if not image_files or image_files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        if not allowed_file_size(image_files):
            return jsonify({'error': 'Total file size exceeds 4.5MB limit'}), 400

        images = []
        for image in image_files:
            if image and allowed_file(image.filename, ['png', 'jpg', 'jpeg', 'bmp', 'gif']):
                try:
                    img_stream = io.BytesIO(image.read())
                    images.append(Image.open(img_stream).convert('RGB'))
                except Exception as e:
                    return jsonify({'error': 'Invalid or corrupted image file'}), 400

        if images:
            pdf_stream = io.BytesIO()
            images[0].save(pdf_stream, save_all=True, append_images=images[1:], format='PDF')
            pdf_stream.seek(0)

        return send_file(pdf_stream, as_attachment=True, download_name='images.pdf')
    except Exception as e:
        app.logger.error(f"Error in image_to_pdf: {str(e)}")
        return jsonify({'error': 'Failed to convert images to PDF'}), 500

@app.route('/encrypt_pdf', methods=['POST'])
def encrypt_pdf():
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        pdf_file = request.files['pdf_file']
        password = request.form.get('password')
        if not pdf_file or pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file_size([pdf_file]):
            return jsonify({'error': 'File size exceeds 4.5MB limit'}), 400

        if pdf_file and allowed_file(pdf_file.filename, ['pdf']):
            try:
                pdf_stream = io.BytesIO(pdf_file.read())
                reader = PdfReader(pdf_stream)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.encrypt(password)

                encrypted_pdf_stream = io.BytesIO()
                writer.write(encrypted_pdf_stream)
                encrypted_pdf_stream.seek(0)

                return send_file(encrypted_pdf_stream, as_attachment=True, download_name='encrypted.pdf')
            except Exception as e:
                return jsonify({'error': 'Invalid or corrupted PDF file'}), 400
    except Exception as e:
        app.logger.error(f"Error in encrypt_pdf: {str(e)}")
        return jsonify({'error': 'Failed to encrypt PDF'}), 500

ALLOWED_EXTENSIONS = {'pdf'}

@app.route('/pdf_to_image', methods=['POST'])
def pdf_to_image():
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        pdf_file = request.files['pdf_file']

        if not pdf_file or pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file_size([pdf_file]):
            return jsonify({'error': 'File size exceeds 4.5MB limit'}), 400

        if not allowed_file(pdf_file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

        try:
            # Convert PDF to images
            pdf_bytes = pdf_file.read()
            images = convert_pdf_to_images(pdf_bytes)

            # Create a zip file in memory
            memory_zip = io.BytesIO()
            with zipfile.ZipFile(memory_zip, 'w') as zipf:
                for i, img_stream in enumerate(images):
                    img_stream.seek(0)  # Ensure the stream is at the start
                    zipf.writestr(f'page_{i + 1}.jpg', img_stream.read())

            # Prepare the zip file for sending
            memory_zip.seek(0)
            return send_file(
                memory_zip,
                mimetype='application/zip',
                as_attachment=True,
                download_name='extracted_images.zip'
            )
        except Exception as e:
            return jsonify({'error': 'Failed to convert PDF to images'}), 500
    except Exception as e:
        app.logger.error(f"Error in pdf_to_image: {str(e)}")
        return jsonify({'error': 'Failed to convert PDF to images'}), 500

@app.route('/split_pdf', methods=['POST'])
def split_pdf():
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        pdf_file = request.files['pdf_file']
        if not pdf_file or pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file_size([pdf_file]):
            return jsonify({'error': 'File size exceeds 4.5MB limit'}), 400

        start_page = int(request.form['start_page'])
        end_page = int(request.form['end_page'])

        if start_page < 1 or end_page < start_page:
            return jsonify({'error': 'Invalid page numbers'}), 400

        if pdf_file and allowed_file(pdf_file.filename, ['pdf']):
            try:
                pdf_stream = io.BytesIO(pdf_file.read())
                pdf_reader = PdfReader(pdf_stream)
                pdf_writer = PdfWriter()

                # Adjust page numbers to 0-based index
                start_idx = start_page - 1
                end_idx = min(end_page, len(pdf_reader.pages))

                for page_num in range(start_idx, end_idx):
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)

                output_stream = io.BytesIO()
                pdf_writer.write(output_stream)
                output_stream.seek(0)

                return send_file(
                    output_stream,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='split.pdf'
                )
            except Exception as e:
                app.logger.error(f"Split PDF error: {str(e)}")
                return jsonify({'error': 'Invalid or corrupted PDF file'}), 400
    except Exception as e:
        app.logger.error(f"Error in split_pdf: {str(e)}")
        return jsonify({'error': 'Failed to split PDF'}), 500

@app.route('/split_pdf_specific_pages', methods=['POST'])
def split_pdf_specific_pages():
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        pdf_file = request.files['pdf_file']
        pages = request.form.get('pages')
        if not pdf_file or pdf_file.filename == '' or not pages:
            return jsonify({'error': 'No file selected or pages not specified'}), 400
        
        if not allowed_file_size([pdf_file]):
            return jsonify({'error': 'File size exceeds 4.5MB limit'}), 400

        pages = [int(page) - 1 for page in pages.split(',')]

        if pdf_file and allowed_file(pdf_file.filename, ['pdf']):
            try:
                pdf_stream = io.BytesIO(pdf_file.read())
                reader = PdfReader(pdf_stream)
                writer = PdfWriter()
                for page_num in pages:
                    writer.add_page(reader.pages[page_num])

                split_pdf_stream = io.BytesIO()
                writer.write(split_pdf_stream)
                split_pdf_stream.seek(0)

                return send_file(split_pdf_stream, as_attachment=True, download_name='split_specific.pdf')
            except Exception as e:
                return jsonify({'error': 'Invalid or corrupted PDF file'}), 400
    except Exception as e:
        app.logger.error(f"Error in split_pdf_specific_pages: {str(e)}")
        return jsonify({'error': 'Failed to split PDF'}), 500

def convert_pdf_to_images(pdf_bytes):
    images = []
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        img_stream = io.BytesIO()
        img.save(img_stream, format='JPEG', quality=95)
        img_stream.seek(0)
        images.append(img_stream)
    
    pdf_document.close()
    return images

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
