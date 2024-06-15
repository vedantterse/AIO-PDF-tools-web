import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, send_from_directory
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
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    if 'pdf_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    pdf_files = request.files.getlist('pdf_files')
    if not pdf_files or pdf_files[0].filename == '':
        flash('No selected files')
        return redirect(request.url)

    merger = PdfMerger()
    for pdf in pdf_files:
        if pdf and allowed_file(pdf.filename, ['pdf']):
            pdf_stream = io.BytesIO(pdf.read())
            merger.append(pdf_stream)

    merged_pdf_stream = io.BytesIO()
    merger.write(merged_pdf_stream)
    merger.close()
    merged_pdf_stream.seek(0)

    return send_file(merged_pdf_stream, as_attachment=True, download_name='merged.pdf')


@app.route('/image_to_pdf', methods=['POST'])
def image_to_pdf():
    if 'image_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    image_files = request.files.getlist('image_files')
    if not image_files or image_files[0].filename == '':
        flash('No selected files')
        return redirect(request.url)

    images = []
    for image in image_files:
        if image and allowed_file(image.filename, ['png', 'jpg', 'jpeg', 'bmp', 'gif']):
            img_stream = io.BytesIO(image.read())
            images.append(Image.open(img_stream).convert('RGB'))

    if images:
        pdf_stream = io.BytesIO()
        images[0].save(pdf_stream, save_all=True, append_images=images[1:], format='PDF')
        pdf_stream.seek(0)

    return send_file(pdf_stream, as_attachment=True, download_name='images.pdf')


@app.route('/encrypt_pdf', methods=['POST'])
def encrypt_pdf():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    pdf_file = request.files['pdf_file']
    password = request.form.get('password')
    if not pdf_file or pdf_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if pdf_file and allowed_file(pdf_file.filename, ['pdf']):
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

ALLOWED_EXTENSIONS = {'pdf'}

@app.route('/pdf_to_image', methods=['POST'])
def pdf_to_image():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    pdf_file = request.files['pdf_file']

    if not pdf_file or pdf_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if not allowed_file(pdf_file.filename, ALLOWED_EXTENSIONS):
        flash('Invalid file type. Please upload a PDF file.')
        return redirect(request.url)

    try:
        # Convert PDF to images
        pdf_bytes = pdf_file.read()
        images = convert_pdf_to_images(pdf_bytes)

        # Create a zip file containing all images
        zip_filename = os.path.join('/tmp', 'converted_images.zip')
        create_zip(images, zip_filename)

        # Send the zip file for download
        return send_file(zip_filename, as_attachment=True)

    except Exception as e:
        app.logger.error(f"Error processing PDF: {str(e)}")
        flash(f"Error processing PDF: {str(e)}")
        return redirect(request.url)

def convert_pdf_to_images(pdf_bytes):
    images = []
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_stream = io.BytesIO()
        img.save(img_stream, format='JPEG')
        img_stream.seek(0)
        images.append(img_stream)
    return images

def create_zip(images, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for i, img_stream in enumerate(images):
            img_stream.seek(0)  # Ensure the stream is at the start
            zipf.writestr(f'page_{i + 1}.jpg', img_stream.read())

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
@app.route('/split_pdf', methods=['POST'])
def split_pdf():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    pdf_file = request.files['pdf_file']
    if not pdf_file or pdf_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    start_page = int(request.form['start_page'])
    end_page = int(request.form['end_page'])

    if start_page < 1 or end_page < start_page:
        flash('Invalid page numbers')
        return redirect(request.url)

    if pdf_file and allowed_file(pdf_file.filename, ['pdf']):
        pdf_stream = io.BytesIO(pdf_file.read())
        pdf_reader = PdfReader(pdf_stream)
        pdf_writer = PdfWriter()

        for page_num in range(start_page - 1, min(end_page, len(pdf_reader.pages))):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        split_pdf_stream = io.BytesIO()
        pdf_writer.write(split_pdf_stream)
        split_pdf_stream.seek(0)

    return send_file(split_pdf_stream, as_attachment=True, download_name='split.pdf')


@app.route('/split_pdf_specific_pages', methods=['POST'])
def split_pdf_specific_pages():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    pdf_file = request.files['pdf_file']
    pages = request.form.get('pages')
    if not pdf_file or pdf_file.filename == '' or not pages:
        flash('No selected file or pages')
        return redirect(request.url)

    pages = [int(page) - 1 for page in pages.split(',')]

    if pdf_file and allowed_file(pdf_file.filename, ['pdf']):
        pdf_stream = io.BytesIO(pdf_file.read())
        reader = PdfReader(pdf_stream)
        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num])

        split_pdf_stream = io.BytesIO()
        writer.write(split_pdf_stream)
        split_pdf_stream.seek(0)

    return send_file(split_pdf_stream, as_attachment=True, download_name='split_specific.pdf')


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,)
