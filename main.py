from flask import Flask, render_template, request, jsonify
from google.cloud import vision
import google.auth
import json
import os
import io
import openai
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
import pandas as pd
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy eklendi

app = Flask(__name__, static_folder='static')

# DATABASE_URL, Heroku'daki Config Vars'tan alınacak
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanı işlemleri için SQLAlchemy örneği
db = SQLAlchemy(app)

# User modeli, API Key ve email adresini saklayacak
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)  # Ad eklendi
    last_name = db.Column(db.String(50), nullable=False)   # Soyad eklendi
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)   # Şifre eklendi

    def __repr__(self):
        return f'<User {self.email}>'

# ApiKey modeli, User tablosuyla ilişkilendirilmiş
class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(255), nullable=False)
    criteria = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('api_keys', lazy=True))

    def __repr__(self):
        return f'<ApiKey {self.api_key}>'

# Google Cloud Vision istemcisini oluşturma
def create_vision_client():
    credentials_info = json.loads(os.environ.get('GOOGLE_CREDENTIALS', '{}'))
    if credentials_info:
        credentials, project = google.auth.load_credentials_from_dict(credentials_info)
        client = vision.ImageAnnotatorClient(credentials=credentials)
        return client
    else:
        raise EnvironmentError("GOOGLE_CREDENTIALS environment variable not set.")

# Görsel dosyasını analiz etme fonksiyonu
def analyze_image_with_vision(image_file):
    content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    extracted_text = ""
    if texts:
        extracted_text = texts[0].description
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
    system_message = {
        "role": "system",
        "content": f"Product listing expert for {platform}. The category is {category}."
    }
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
            messages=[system_message, {"role": "user", "content": prompt}]
        )
        result_text = response['choices'][0]['message']['content']
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

# Kategori ve ülke bilgilerini .txt dosyalarından okuma
def load_data_from_txt(file_name):
    with open(file_name, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Ana sayfa (upload.html)
@app.route('/')
def home():
    categories = load_data_from_txt('category.txt')  # Kategoriler category.txt dosyasından alınacak
    countries = load_data_from_txt('countries.txt')  # Ülkeler countries.txt dosyasından alınacak
    return render_template('upload.html', categories=categories, countries=countries)  # upload.html ana sayfa olacak

# Profil Sayfası (index.html dosyasına yönlendirilmiş)
@app.route('/profile')
def profile():
    return render_template('index.html')  # index.html profil sayfası olarak kalacak

# Kullanıcı Oluşturma Sayfası (profile.html)
@app.route('/create_profile', methods=['POST', 'GET'])
def create_profile():
    if request.method == 'POST':
        first_name = request.form['first_name']  # Ad eklendi
        last_name = request.form['last_name']    # Soyad eklendi
        email = request.form['email']
        password = request.form['password']  # Şifre eklendi
        api_key = request.form['apiKey']
        
        # Yeni kullanıcıyı veritabanına ekle
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, api_key=api_key)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully!'})
    return render_template('profile.html')  # profile.html kullanıcı oluşturma ekranı

# API Key ve kriter kaydetme rotası
@app.route('/submit_apikey', methods=['POST'])
def submit_apikey():
    api_key = request.form['apiKey']
    criteria = request.form['criteria']
    user_id = request.form['user_id']  # Kullanıcının ID'si bu formdan gelecek

    # Verilerin doğru geldiğini kontrol etmek için print ekliyoruz.
    print(f"API Key: {api_key}, Criteria: {criteria}, User ID: {user_id}")

    # API Key ve kriter verilerini kaydet
    new_apikey = ApiKey(api_key=api_key, criteria=criteria, user_id=user_id)
    db.session.add(new_apikey)
    db.session.commit()

    return jsonify({'message': 'API Key and criteria saved successfully!'})

# Upload sayfası
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            file = request.files['file']
            platform = request.form['platform']
            additional_info = request.form.get('additionalInfo', '')
            api_key = request.form['apiKey']
            platform_criteria = request.form['platformCriteria']
            category = request.form.get('category', '')

            if not file or not platform or not api_key or not platform_criteria or not category:
                missing_fields = []
                if not file: missing_fields.append('file')
                if not platform: missing_fields.append('platform')
                if not api_key: missing_fields.append('apiKey')
                if not platform_criteria: missing_fields.append('platformCriteria')
                if not category: missing_fields.append('category')
                return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

            if file.filename.endswith(('.png', '.jpg', '.jpeg')):
                text = analyze_image_with_vision(file)
            elif file.filename.endswith('.pdf'):
                text = analyze_pdf(file)
            elif file.filename.endswith('.docx'):
                text = analyze_docx(file)
            else:
                return jsonify({"error": "Unsupported file type."}), 400

            response_text = analyze_text_with_ai(text, platform, platform_criteria, category, additional_info, api_key)
            return response_text

        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    else:
        categories = load_data_from_txt('category.txt')  # Kategoriler category.txt dosyasından alınacak
        countries = load_data_from_txt('countries.txt')  # Ülkeler countries.txt dosyasından alınacak
        return render_template('upload.html', categories=categories, countries=countries)

if __name__ == "__main__":
    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 5000))  # Heroku'nun sağlayacağı PORT değişkenini kullan
    app.run(debug=True, host="0.0.0.0", port=port)
