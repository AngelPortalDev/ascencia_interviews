# from django.views.decorators.csrf import csrf_exempt
# from google.cloud import vision
# from transformers import pipeline
# import spacy
# import pytesseract
# import cv2
# from django.http import JsonResponse
# from PIL import Image
# import numpy as np
# from spellchecker import SpellChecker

# # Load SpaCy's pre-trained NER model
# nlp = spacy.load("en_core_web_sm")
# classifier = pipeline("zero-shot-classification")

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Preprocess the image (enhanced)
# def preprocess_image(uploaded_file):
#     image = Image.open(uploaded_file)
#     img = np.array(image)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#     binary_img = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
#     resized_img = cv2.resize(binary_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
#     return resized_img

# # OCR extraction using Google Vision
# def extract_text_with_google_vision(image):
#     client = vision.ImageAnnotatorClient()
#     image_content = image.tobytes()
#     image = vision.types.Image(content=image_content)
#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#     return texts[0].description if texts else ""

# # Correct OCR text with SpellChecker
# def correct_text(text):
#     spell = SpellChecker()
#     words = text.split()
#     corrected_text = " ".join([spell.correction(word) for word in words])
#     return corrected_text

# # Document Classification using Hugging Face
# def classify_document(extracted_text):
#     labels = ["Passport", "Invoice", "Receipt", "ID Card", "Driver's License", "Certificate", "Contract", "Bank Document"]
#     result = classifier(extracted_text, candidate_labels=labels)
#     return result['labels'][0], result['scores'][0]

# # Named Entity Recognition
# def extract_named_entities(extracted_text):
#     doc = nlp(extracted_text)
#     named_entities = {}
#     for ent in doc.ents:
#         named_entities[ent.text] = ent.label_
#     return named_entities

# # Main function
# @csrf_exempt
# def process_lead(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES.get('document')

#         if uploaded_file:
#             try:
#                 if uploaded_file.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
#                     return JsonResponse({"error": "Invalid file format. Only image files are allowed."}, status=400)
                
#                 # Preprocess image
#                 image = preprocess_image(uploaded_file)

#                 # Extract text with Google Vision
#                 extracted_text = extract_text_with_google_vision(image)

#                 # Correct OCR errors
#                 extracted_text = correct_text(extracted_text)

#                 # Classify document type
#                 document_type, confidence_score = classify_document(extracted_text)

#                 # Extract named entities
#                 named_entities = extract_named_entities(extracted_text)

#                 return JsonResponse({
#                     "message": "Data processed successfully",
#                     "extracted_text": extracted_text,
#                     "named_entities": named_entities,
#                     "document_type": document_type,
#                     "confidence_score": confidence_score
#                 }, status=200)

#             except Exception as e:
#                 return JsonResponse({"error": str(e)}, status=500)

#         else:
#             return JsonResponse({"error": "No document uploaded"}, status=400)
#     else:
#         return JsonResponse({"error": "Only POST requests allowed"}, status=405)

























from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
import pytesseract
import cv2
import numpy as np
import spacy
import re
from transformers import pipeline
import logging
from pdf2image import convert_from_bytes  # For PDF support
import fitz  # PyMuPDF for advanced PDF handling

# Set the Tesseract command location
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load SpaCy's pre-trained NER model
nlp = spacy.load("en_core_web_sm")

# Initialize Hugging Face zero-shot classification pipeline
classifier = pipeline("zero-shot-classification")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Preprocess the image for better OCR results
def preprocess_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary_img = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    resized_img = cv2.resize(binary_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized_img

# OCR extraction function using Tesseract with multi-language support
def extract_text_with_tesseract(image, lang='eng'):
    custom_config = r'--oem 3 --psm 6'  # Optimized configuration
    extracted_text = pytesseract.image_to_string(image, config=custom_config, lang=lang)
    return extracted_text

# Classify the document type with global support
def classify_document(extracted_text):
    labels = [
        "Passport", "Passeport", "Pasaporte", "Reisepass", "Passaporto", "Паспорт", "جواز سفر", "护照", 
        "パスポート", "여권", "पासपोर्ट", "پاسپورٹ", "Paspoorte", "پاسپورت", 
        "Education Certificate", "Degree Certificate", "Diploma Certificate", "Academic Transcript", 
        "Higher Education Diploma", "Graduate Certificate", "Postgraduate Certificate", 
        "Secondary School Certificate", "High School Diploma", "Bachelor's Degree", "Master's Degree", 
        "PhD Diploma", "Baccalauréat", "Certificado de Estudios", "Zeugnis", "Diploma di Laurea", 
        "شهادة تعليمية", "毕业证书", "학위 증명서", "प्रमाणपत्र", 
        "Resume", "CV", "Curriculum Vitae", "Bio-data", "Professional Profile", "Job Application Form", 
        "Employment History", "Dossier de Candidature", "Hoja de Vida", "Lebenslauf", "Currículo", 
        "سيرة ذاتية", "履歴書", "이력서", "रिज्यूमे"
    ]
    result = classifier(extracted_text, candidate_labels=labels)
    return result['labels'][0], result['scores'][0]

# Extract named entities using SpaCy and regex

def extract_named_entities(text):
    """
    Extracts possible Name, Date of Birth, ID Number, and Address from a given text.
    Handles multiple languages and formats.
    """
    
    # Initialize entities with None as default values
    entities = {
        "Name": None,
        "Date of Birth": None,
        "ID Number": None,
        "Address": None,
    }

    # Possible variations for name fields
    name_variations = [
        "Name", "Full Name", "Nom", "Nombre", "Nome", "Naam", "名前", "이름", "اسم"
    ]
    
    # Possible variations for DOB fields
    dob_variations = [
        "Date of Birth", "DOB", "Birth Date", "Fecha de Nacimiento", "Geburtsdatum",
        "Data de Nascimento", "تاريخ الميلاد", "生年月日", "出生日期", "생년월일"
    ]
    
    # Possible variations for ID fields
    id_variations = [
        "ID Number", "Identification Number", "Passport No", "National ID", "Número de Identificación",
        "Numéro d'Identité", "رقم الهوية", "身分證號", "ID 번호"
    ]
    
    # Possible variations for Address fields
    address_variations = [
        "Address", "Adresse", "Dirección", "Endereço", "عنوان", "住址", "주소"
    ]
    
    # Extract Name using SpaCy's Named Entity Recognition (NER)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":  # SpaCy's PERSON entity for names
            entities["Name"] = ent.text
            break

    # Extract Date of Birth (DOB) using regex
    dob_regex = r"(?i)(" + "|".join(dob_variations) + r")\s*[:\-]?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4})"
    dob_match = re.search(dob_regex, text)
    if dob_match:
        entities["Date of Birth"] = dob_match.group(2)

    # Extract ID Number
    id_regex = r"(?i)(" + "|".join(id_variations) + r")\s*[:\-]?\s*([\w\d\-]+)"
    id_match = re.search(id_regex, text)
    if id_match:
        entities["ID Number"] = id_match.group(2)

    # Extract Address
    address_regex = r"(?i)(" + "|".join(address_variations) + r")\s*[:\-]?\s*([\w\s,.-]+(?:\s*\d{3,6})?)"
    address_match = re.search(address_regex, text)
    if address_match:
        entities["Address"] = address_match.group(2)

    return entities

# Main function to handle POST request and process the uploaded document
@csrf_exempt
def process_lead(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('document')

        if uploaded_file:
            try:
                # Only allow specific file types
                if uploaded_file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
                    return JsonResponse({"error": "Invalid file format. Only image and PDF files are allowed."}, status=400)

                extracted_text = ""
                if uploaded_file.content_type == "application/pdf":
                    # Convert PDF to images using PyMuPDF
                    pdf_data = uploaded_file.read()
                    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        processed_image = preprocess_image(img)
                        extracted_text += extract_text_with_tesseract(Image.fromarray(processed_image)) + "\n"
                else:
                    # Process image files
                    image = Image.open(uploaded_file)
                    processed_image = preprocess_image(image)
                    extracted_text = extract_text_with_tesseract(Image.fromarray(processed_image))

                # Classify the document type
                document_type, confidence_score = classify_document(extracted_text)

                # Extract named entities
                named_entities = extract_named_entities(extracted_text)

                return JsonResponse({
                    "message": "Data processed successfully",
                    "extracted_text": extracted_text,
                    "document_type": document_type,
                    "confidence_score": confidence_score,
                    "named_entities": named_entities
                }, status=200)

            except Exception as e:
                logging.error(f"Error processing document: {str(e)}")
                return JsonResponse({"error": "An internal error occurred. Please try again later."}, status=500)

        else:
            return JsonResponse({"error": "No document uploaded"}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)