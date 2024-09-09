from flask import Flask, render_template, request, jsonify
from google.cloud import vision
import io
import openai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
from trends import get_trends_data, get_trends_related_queries
from visualization import plot_trends, get_plotly_graph_json  # visualization.py dosyasından import
import pandas as pd

app = Flask(__name__, static_folder='static')

# Google Cloud Vision istemcisini oluşturma
client = vision.ImageAnnotatorClient()

# Görsel dosyasını analiz etme fonksiyonu
def analyze_image_with_vision(image_file):
    content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    extracted_text = ""
    if texts:
        extracted_text = texts[0].description  # İlk metin bloğunu alır

    return extracted_text

# PDF dosyasını analiz etme fonksiyonu
def analyze_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()
        return extracted_text
    except Exception as e:
        return f"PDF error: {str(e)}"

# DOCX dosyasını analiz etme fonksiyonu
def analyze_docx(docx_file):
    doc = Document(docx_file)
    extracted_text = ""
    for para in doc.paragraphs:
        extracted_text += para.text + "\n"
    return extracted_text

# AI ile metin analizi yapma fonksiyonu (başlık, açıklama, alt metin ve anahtar kelimeleri üretir)
def analyze_text_with_ai(extracted_text, platform, platform_criteria, category, additional_info, api_key):
    openai.api_key = api_key  # API anahtarını formdan al

    # Dinamik sistem mesajını oluştur
    system_message = {
        "role": "system",
        "content": f"Product listing expert for {platform}. The category is {category}."
    }

    # Yapay zeka için prompt oluşturma
    prompt = f"""
    Platform: {platform}
    Category: {category}
    Criteria: {platform_criteria}
    Additional Info: {additional_info}
    
    Extracted Text: {extracted_text}

    Generate:
    - Title
    - Description
    - Alt text
    - Keywords
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                system_message,  # Dinamik sistem mesajı burada kullanılıyor
                {"role": "user", "content": prompt}
            ]
        )

        # AI'den dönen cevabı ayırarak JSON formatında başlık, açıklama, alt metin ve anahtar kelimeleri geri döndür
        result_text = response['choices'][0]['message']['content']
        # Yapılandırılmış bir JSON cevabı olarak parçala
        result_parts = {
            "title": "Title: " + result_text.split("Title:")[1].split("Description:")[0].strip(),
            "description": "Description: " + result_text.split("Description:")[1].split("Alt text:")[0].strip(),
            "alt_text": "Alt text: " + result_text.split("Alt text:")[1].split("Keywords:")[0].strip(),
            "keywords": "Keywords: " + result_text.split("Keywords:")[1].strip()
        }

        return jsonify(result_parts)

    except openai.error.OpenAIError as e:
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Ana sayfa
@app.route('/')
def serve_home():
    return render_template('index.html')

# Hem GET hem de POST metodunu destekleyen upload rotası
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Formdan dosya ve diğer bilgileri alıyoruz
            file = request.files['file']
            platform = request.form['platform']
            additional_info = request.form.get('additionalInfo', '')
            api_key = request.form['apiKey']
            platform_criteria = request.form['platformCriteria']
            category = request.form.get('category', '')  # Kategori bilgisini alıyoruz

            if not file or not platform or not api_key or not platform_criteria or not category:
                missing_fields = []
                if not file: missing_fields.append('file')
                if not platform: missing_fields.append('platform')
                if not api_key: missing_fields.append('apiKey')
                if not platform_criteria: missing_fields.append('platformCriteria')
                if not category: missing_fields.append('category')
                return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

            # Dosyanın türünü kontrol ediyoruz
            if file.filename.endswith(('.png', '.jpg', '.jpeg')):
                text = analyze_image_with_vision(file)
            elif file.filename.endswith('.pdf'):
                text = analyze_pdf(file)
            elif file.filename.endswith('.docx'):
                text = analyze_docx(file)
            else:
                return jsonify({"error": "Unsupported file type."}), 400

            # Metni platforma özel kriterlerle AI'ye gönder
            response_text = analyze_text_with_ai(text, platform, platform_criteria, category, additional_info, api_key)
            return response_text

        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    else:
        # GET isteği yapıldığında upload.html sayfasını render et
        return render_template('upload.html')

if __name__ == "__main__":
    app.run(debug=True, port=3000)
