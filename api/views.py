# import pytesseract
# import re
# import cv2
# import numpy as np
# from PIL import Image
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import logging
# import fitz  # PyMuPDF for handling PDFs

# # Set the Tesseract command location
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Preprocess the image for better OCR results
# def preprocess_image(image):
#     img = np.array(image)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     # Apply Gaussian blur to reduce noise
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#     # Apply adaptive thresholding
#     binary_img = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
#     # Resize the image for better OCR accuracy
#     resized_img = cv2.resize(binary_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
#     return resized_img


# def extract_text_from_pdf(pdf_data):
#     extracted_text = ""
#     pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         pix = page.get_pixmap()
        
#         # Convert PDF page to grayscale image
#         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("L")
        
#         # Extract MRZ text
#         extracted_text += extract_mrz_text(img) + "\n"

#     return extracted_text.strip()

# def clean_mrz_text(text):
#     # Remove spaces and invalid characters
#     text = re.sub(r'[^A-Z0-9<]', '', text.replace(" ", ""))
    
#     # Ensure two-line format
#     lines = text.split("\n")
#     if len(lines) >= 2:
#         return f"{lines[0]}\n{lines[1]}"
#     return text



# def extract_mrz_text(image):
#     processed_image = preprocess_image(image)
#     extracted_text = pytesseract.image_to_string(
#         Image.fromarray(processed_image), 
#         config="--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
#     )
#     return clean_mrz_text(extracted_text)


# def parse_mrz(mrz_text):
#     # Clean up the MRZ text
#     mrz_text = mrz_text.replace("\n", "")
#     # mrz_text = re.sub(r'[^A-Z0-9<]', '', mrz_text)  # Only keep A-Z, 0-9, and '<'
#     mrz_text = re.sub(r'[^A-Z0-9<\n]', '', mrz_text)


#     # Check if the MRZ text starts with 'P<' (Type 3 passport)
#     if mrz_text.startswith("P<"):
#         # Parse Type 3 (TD3) MRZ
#         lines = mrz_text.split('<')
#         if len(lines) >= 2:
#             country_code = lines[0][2:5]  # Country code (positions 2-4)
#             surname = lines[1]  # Surname (first part after '<')
#             given_names = lines[2]  # Given names (second part after '<')
#             passport_number = lines[3][:9]  # Passport number (first 9 characters)
#             nationality = lines[3][9:12]  # Nationality (positions 10-12)
#             date_of_birth = lines[3][12:18]  # Date of birth (positions 13-18)
#             gender = lines[3][18]  # Gender (position 19)
#             expiration_date = lines[3][19:25]  # Expiration date (positions 20-25)
#             optional_data = lines[3][25:]  # Optional data (positions 26+)

#             return {
#                 "country_code": country_code,
#                 "surname": surname,
#                 "given_names": given_names,
#                 "passport_number": passport_number,
#                 "nationality": nationality,
#                 "date_of_birth": date_of_birth,
#                 "gender": gender,
#                 "expiration_date": expiration_date,
#                 "optional_data": optional_data,
#             }
#         else:
#             raise ValueError("Invalid MRZ format: Not enough parts.")
#     else:
#         raise ValueError("Invalid MRZ format: Does not start with 'P<'.")


# # Format MRZ text for better structure
# def format_mrz(mrz_text):
#     logging.info(f"Raw MRZ Text: {mrz_text}")

#     # Clean up the MRZ text, remove unwanted characters
#     mrz_text = mrz_text.replace("\n", "")
#     mrz_text = re.sub(r'[^A-Z0-9<]', '', mrz_text)  # Only keep A-Z, 0-9, and '<'

#     # Ensure MRZ starts with 'P<' (Type 3 passport)
#     if not mrz_text.startswith("P<"):
#         logging.error(f"Invalid MRZ format: Does not start with 'P<'. MRZ Text: {mrz_text}")
#         raise ValueError("Invalid MRZ format: Does not start with 'P<'.")

#     # Split the MRZ text into lines (assuming two lines for Type 3)
#     lines = mrz_text.split('<')
#     if len(lines) < 2:
#         logging.error(f"Invalid MRZ format: Not enough lines. MRZ Text: {mrz_text}")
#         raise ValueError("Invalid MRZ format: Not enough lines.")

#     # Extract fields from the first line
#     first_line = lines[0]
#     country_code = first_line[2:5]  # Country code (positions 2-4)
#     surname = lines[1]  # Surname (first part after '<')
#     given_names = lines[2]  # Given names (second part after '<')

#     # Extract fields from the second line
#     second_line = lines[3]
#     passport_number = second_line[:9]  # Passport number (first 9 characters)
#     nationality = second_line[9:12]  # Nationality (positions 10-12)
#     date_of_birth = second_line[12:18]  # Date of birth (positions 13-18)
#     gender = second_line[18]  # Gender (position 19)
#     expiration_date = second_line[19:25]  # Expiration date (positions 20-25)
#     optional_data = second_line[25:]  # Optional data (positions 26+)

#     # Format the extracted data
#     formatted_text = (
#         f"Country Code: {country_code}\n"
#         f"Surname: {surname}\n"
#         f"Given Names: {given_names}\n"
#         f"Passport Number: {passport_number}\n"
#         f"Nationality: {nationality}\n"
#         f"Date of Birth: {date_of_birth}\n"
#         f"Gender: {gender}\n"
#         f"Expiration Date: {expiration_date}\n"
#         f"Optional Data: {optional_data}"
#     )

#     return formatted_text




# # Process uploaded document
# @csrf_exempt
# def process_lead(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES.get('document')

#         if uploaded_file:
#             try:
#                 # Only allow specific file types
#                 if uploaded_file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
#                     return JsonResponse({"error": "Invalid file format. Only image and PDF files are allowed."}, status=400)

#                 extracted_text = ""
#                 if uploaded_file.content_type == "application/pdf":
#                     # Convert PDF to images using PyMuPDF
#                     pdf_data = uploaded_file.read()
#                     pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
#                     for page_num in range(len(pdf_document)):
#                         page = pdf_document.load_page(page_num)
#                         pix = page.get_pixmap()
#                         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                         extracted_text += extract_mrz_text(img) + "\n"
#                 else:
#                     # Process image files
#                     image = Image.open(uploaded_file)
#                     extracted_text = extract_mrz_text(image)

#                 # Check if extracted text is empty
#                 if not extracted_text:
#                     return JsonResponse({"error": "MRZ text not found in document"}, status=400)

#                 # Parse the MRZ text
#                 try:
#                     mrz_data = parse_mrz(extracted_text)
#                 except ValueError as e:
#                     logging.error(f"Error parsing MRZ text: {str(e)}")
#                     return JsonResponse({"error": str(e)}, status=400)

#                 return JsonResponse({
#                     "message": "Data processed successfully",
#                     "extracted_data": extracted_text,
#                     "mrz_data": mrz_data,
#                 }, status=200)

#             except Exception as e:
#                 logging.error(f"Error processing document: {str(e)}")
#                 return JsonResponse({"error": "An internal error occurred. Please try again later."}, status=500)

#         else:
#             return JsonResponse({"error": "No document uploaded"}, status=400)
#     else:
#         return JsonResponse({"error": "Only POST requests allowed"}, status=405)    































import pytesseract
import re
import cv2
import numpy as np
from PIL import Image
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import fitz  # PyMuPDF
import easyocr
import pycountry

reader = easyocr.Reader(["en"])

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Preprocess image
def preprocess_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    binary_img = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return binary_img


# Extract text from image
def extract_text_from_image(image):
    img = np.array(image)
    results = reader.readtext(img, detail=0)  # Using EasyOCR
    return " ".join(results)


# Extract text from PDF
def extract_text_from_pdf(pdf_data):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    extracted_text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("L")
        extracted_text += extract_text_from_image(img) + "\n"

    return extracted_text.strip()

# Extract name from MRZ
def extract_surname_from_mrz(text):
    mrz_pattern = r"P<([A-Z]{3})([A-Z0-9<]+)<<([A-Z0-9]+)"
    match = re.search(mrz_pattern, text)
    if match:
        surname = match.group(2).replace("<", "")
        name = match.group(3).replace("<", "")
        return surname, name 
    return None, None
    
    
# Extract DOB and Expiry Date from MRZ
def extract_dob_and_doe_from_mrz(text):
    # Pattern to match the DOB and expiry date in the MRZ (YYMMDD format), and capture the extra digit before gender
    dob_pattern = r"(\d{6,7})([MF])(\d{6})"

    # Search for the DOB pattern in the entire text
    match = re.search(dob_pattern, text)

    if match:
        # Extract the DOB and expiry date from the match groups
        dob_digits = match.group(1)  # First 6 or 7 digits, representing DOB in YYMMDD format
        gender_char = match.group(2)  # Gender character (M or F)
        expiry_digits = match.group(3)  # The next 6 digits, representing expiry date in YYMMDD format
        
        # Check if DOB digits have 6 or 7 characters
        if len(dob_digits) == 6:
            # For 6 digits, use the first 2 for the year, the next 2 for the month, and the last 2 for the day
            dob_year = "200" + dob_digits[0:1]  # Assuming DOB is in the 2000s (e.g., '03' -> '2003')
            dob_month = dob_digits[1:3]  # Month (e.g., '12')
            dob_day = dob_digits[3:5]  # Day (e.g., '12')
        elif len(dob_digits) == 7:
            # For 7 digits, adjust to skip the extra digit (e.g., '0302151' -> '030215')
            dob_year_prefix = "20" if int(dob_digits[0:2]) <= 50 else "19"
            dob_year = dob_year_prefix + dob_digits[0:2]    # Assuming DOB is in the 2000s (e.g., '03' -> '2003')
            dob_month = dob_digits[2:4]  # Month (e.g., '12')
            dob_day = dob_digits[4:6]  # Day (e.g., '12')

        dob_formatted = f"{dob_year}-{dob_month}-{dob_day}"

        # Extract and format expiry date
        expiry_year = "20" + expiry_digits[0:2]  # Assuming expiry is in the 2000s
        expiry_month = expiry_digits[2:4]
        expiry_day = expiry_digits[4:6]

        expiry_formatted = f"{expiry_year}-{expiry_month}-{expiry_day}"

        # Return DOB and Expiry Date
        return dob_formatted, expiry_formatted
    else:
        return None, None



# Extract passport number from MRZ
def extract_passport_number_from_mrz(text):
    lines = text.split("\n")
    # print(r'lines:', lines)
    
    if len(lines) < 2:
        return None  # Ensure at least two lines exist
    
    second_line = lines[1]  # MRZ second line contains the passport number
    # print(r'second_line:', second_line)
    
    # Passport number patterns
    passport_patterns = [
        r"\b[A-Z]\d{6,9}\b",  # First pattern (e.g., C0018730)
        r"\b[A-Z]{2}\d{7}\b",  # Second pattern (e.g., AB1234567)
        r"\b\d{9}\b"  # Third pattern (e.g., 123456789)
        r"\b[A-Z]{2}\d{6}\b",  # Fourth pattern (e.g., AB123456)
    ]
    
    # Check for matching patterns
    for pattern in passport_patterns:
        match = re.search(pattern, second_line)
        if match:
            return match.group(0)  # Extracted passport number

    return None

# Extract passport number from regular text
def extract_passport_number(text):
    # print(r'text:', text)
    passport_patterns = [
        r"\b[A-Z]{2}\d{7}\b",  # AB1234567
        r"\b[A-Z]{2}\d{6}\b",  # AB123456
        r"\b[A-Z]\d{8}\b",  # A12345678
        r"\b\d{9}\b",  # 123456789
        r"\b[A-Z0-9]{9}\b",  # Alphanumeric passport
        r"\b[A-Z]{3}\d{6}\b"  # ABC123456
    ]

    passport_numbers = []
    for pattern in passport_patterns:
        matches = re.findall(pattern, text)
        passport_numbers.extend(matches)  # Add all matches to the list

    return passport_numbers  # Extracted passport number

    return None


def validate_passport_number(passport_number):
    print(r'passport_number:', passport_number)
    
    # Ensure the passport number is not empty and has a valid length (8 or 9 characters)
    if not passport_number or len(passport_number) not in [8, 9]:
        return False

    # If the passport starts with one or two letters, we handle that case
    if passport_number[0].isalpha():
        # If it starts with two letters, we remove the first two characters for validation
        if len(passport_number) >= 8 and passport_number[1].isalpha():
            passport_number = passport_number[2:]
        else:
            passport_number = passport_number[1:]

    # Now check if the remaining characters are all digits
    if not passport_number.isdigit():
        return False  # Fail if there are non-digit characters remaining

    # If length is 9, consider it a valid passport number
    if len(passport_number) == 9:
        return True  # Passport number is valid if it's 9 digits long

    # If the passport number is valid 8-digit, also accept it
    return True


# Fetch passport number (from MRZ or regular text)
def fetch_passport_number(text):
    passport_number = extract_passport_number_from_mrz(text)

    if passport_number:
        if validate_passport_number(passport_number):
            return passport_number  # Valid passport number from MRZ
        else:
            return None  # Invalid passport number from MRZ
    else:
        # If no passport number from MRZ, check regular extraction
        passport_numbers = extract_passport_number(text)
        
        if passport_numbers:
            for passport_number in passport_numbers:
                if validate_passport_number(passport_number):
                    return passport_number
            return None

    return None  # No passport number found or invalid



# Django view to process uploaded document
@csrf_exempt
def process_document(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("document")
        
        if not uploaded_file:
            return JsonResponse({"error": "No document uploaded"}, status=400)

        try:
            if uploaded_file.content_type == "application/pdf":
                pdf_data = uploaded_file.read()
                extracted_text = extract_text_from_pdf(pdf_data)
            else:
                image = Image.open(uploaded_file)
                extracted_text = extract_text_from_image(image)

            surname, name = extract_surname_from_mrz(extracted_text)
            passport_number = fetch_passport_number(extracted_text)
            dob, expire_date = extract_dob_and_doe_from_mrz(extracted_text)

            return JsonResponse({
                "message": "Success", 
                "extracted_text": extracted_text, 
                "surname": surname, 
                "given_name": name, 
                "passport_number": passport_number, 
                "dob": dob,
                "expire_date": expire_date,
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": "An error occurred: " + str(e)}, status=500)
    
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)









































































# import re
# import logging
# import numpy as np
# import easyocr
# import spacy
# import cv2
# from PIL import Image
# from transformers import pipeline
# import fitz
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# # Initialize EasyOCR Reader and Spacy NLP model
# reader = easyocr.Reader(['en'])
# nlp = spacy.load("en_core_web_sm")
# classifier = pipeline("zero-shot-classification")

# # Setup logging
# logging.basicConfig(level=logging.INFO)

# def preprocess_image(image):
#     """
#     Preprocess image to enhance OCR accuracy.
#     """
#     img = np.array(image)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#     binary_img = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
#     resized_img = cv2.resize(binary_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
#     return resized_img

# def extract_text_with_easyocr(image):
#     """
#     Extract text from an image using EasyOCR.
#     """
#     result = reader.readtext(np.array(image))
#     extracted_text = ' '.join([item[1] for item in result])
#     return extracted_text

# def classify_document(extracted_text):
#     """
#     Classify the document type based on the extracted text.
#     """
#     labels = [
#         "Passport", "Passeport", "Pasaporte", "Reisepass", "Passaporto", "Паспорт", "جواز سفر", "护照",
#         "パスポート", "여권", "पासपोर्ट", "پاسپورٹ", "Paspoorte", "پاسپورت", 
#         "Education Certificate", "Degree Certificate", "Diploma Certificate", "Academic Transcript",
#         "Resume", "CV", "Curriculum Vitae", "Bio-data", "Professional Profile", "Job Application Form",
#     ]
#     result = classifier(extracted_text, candidate_labels=labels)
#     return result['labels'][0]

# def extract_passport_number(text):
#     """Extract passport number (1 letter followed by 7-9 digits)."""
#     pattern = r'\b[A-Z][0-9]{7,9}\b'
#     match = re.search(pattern, text)
#     return match.group(0) if match else None

# def extract_name(text):
#     """Extract name based on known passport text structure."""
#     pattern = r'(?:Surname|Nom)[\s:]([A-Za-z\s\-]+)\s(?:Given Names|Prenoms)[\s:]*([A-Za-z\s\-]+)'
    
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         surname = match.group(1).strip()
#         given_names = match.group(2).strip()
#         return f"{surname} {given_names}"
#     return None

# @csrf_exempt
# def process_lead(request):
#     """
#     API endpoint to process uploaded documents and extract details.
#     """
#     if request.method == "POST":
#         uploaded_file = request.FILES.get('document')

#         if uploaded_file:
#             try:
#                 if uploaded_file.content_type not in ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']:
#                     return JsonResponse({"error": "Invalid file format. Only image and PDF files are allowed."}, status=400)

#                 extracted_text = ""
#                 if uploaded_file.content_type == "application/pdf":
#                     pdf_data = uploaded_file.read()
#                     pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
#                     for page_num in range(len(pdf_document)):
#                         page = pdf_document.load_page(page_num)
#                         pix = page.get_pixmap()
#                         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                         processed_image = preprocess_image(img)
#                         extracted_text += extract_text_with_easyocr(Image.fromarray(processed_image)) + "\n"
#                 else:
#                     image = Image.open(uploaded_file)
#                     processed_image = preprocess_image(image)
#                     extracted_text = extract_text_with_easyocr(Image.fromarray(processed_image))

#                 document_type = classify_document(extracted_text)
#                 passport_number = extract_passport_number(extracted_text)
#                 name = extract_name(extracted_text)

#                 return JsonResponse({
#                     "message": "Data processed successfully",
#                     "extracted_text": extracted_text,
#                     "document_type": document_type,
#                     "passport_number": passport_number,
#                     "name": name,
#                 }, status=200)

#             except Exception as e:
#                 logging.error(f"Error processing document: {str(e)}")
#                 return JsonResponse({"error": "An internal error occurred. Please try again later."}, status=500)

#         else:
#             return JsonResponse({"error": "No document uploaded"}, status=400)
#     else:
#         return JsonResponse({"error": "Only POST requests allowed"}, status=405)




























































# import os
# import traceback
# import tempfile
# import textract
# import spacy
# import re
# from transformers import pipeline
# import logging
# import pytesseract
# from PIL import Image
# from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# # Load SpaCy's pre-trained NER model
# nlp = spacy.load("en_core_web_sm")

# # Initialize Hugging Face zero-shot classification pipeline
# classifier = pipeline("zero-shot-classification")

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# def extract_text(file, content_type):
#     """Extracts text from uploaded document."""
#     try:
#         temp_file_path = None

#         # If file is in memory, write to temp file
#         if isinstance(file, InMemoryUploadedFile) or isinstance(file, TemporaryUploadedFile):
#             temp_file = tempfile.NamedTemporaryFile(delete=False)
#             for chunk in file.chunks():
#                 temp_file.write(chunk)
#             temp_file.close()
#             temp_file_path = temp_file.name
#         else:
#             return ""

#         # Extract text
#         text = ""
#         if content_type in ["application/pdf", "text/plain"]:
#             text = textract.process(temp_file_path).decode("utf-8")
#         elif content_type in ["image/jpeg", "image/png", "image/jpg"]:
#             text = pytesseract.image_to_string(Image.open(temp_file_path))
        
#         os.remove(temp_file_path)  # Cleanup temp file
#         return text.strip()
    
#     except Exception as e:
#         logging.error(f"Error extracting text: {traceback.format_exc()}")
#         return ""

# def classify_document(extracted_text):
#     """Classifies document type."""
#     # labels = ["Passport", "Education Certificate", "Resume"]
#     labels = [
#         "Passport", "Passeport", "Pasaporte", "Reisepass", "Passaporto", "Паспорт", "جواز سفر", "护照", 
#         "パスポート", "여권", "पासपोर्ट", "پاسپورٹ", "Paspoorte", "پاسپورت", 
#         "Education Certificate", "Degree Certificate", "Diploma Certificate", "Academic Transcript", 
#         "Higher Education Diploma", "Graduate Certificate", "Postgraduate Certificate", 
#         "Secondary School Certificate", "High School Diploma", "Bachelor's Degree", "Master's Degree", 
#         "PhD Diploma", "Baccalauréat", "Certificado de Estudios", "Zeugnis", "Diploma di Laurea", 
#         "شهادة تعليمية", "毕业证书", "학위 증명서", "प्रमाणपत्र", 
#         "Resume", "CV", "Curriculum Vitae", "Bio-data", "Professional Profile", "Job Application Form", 
#         "Employment History", "Dossier de Candidature", "Hoja de Vida", "Lebenslauf", "Currículo", 
#         "سيرة ذاتية", "履歴書", "이력서", "रिज्यूमे"
#     ]
#     result = classifier(extracted_text, candidate_labels=labels)
#     return result['labels'][0], result['scores'][0]

# def extract_named_entities(text):
#     """Extracts named entities such as Name, Date of Birth, ID Number, Address."""
#     entities = {"Name": None, "Date of Birth": None, "ID Number": None, "Address": None}
    
#     # SpaCy for name extraction
#     doc = nlp(text)
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             entities["Name"] = ent.text
#             break

#     # Regex-based extraction
#     patterns = {
#         "Date of Birth": r"(DOB|Birth Date)[:\-]?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})",
#         "ID Number": r"(ID Number|Passport No)[:\-]?\s*([\w\d\-]+)",
#         "Address": r"(Address)[:\-]?\s*([\w\s,.-]+)"
#     }
#     for key, pattern in patterns.items():
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             entities[key] = match.group(2)

#     return entities

# @csrf_exempt
# def process_lead(request):
#     """Handles document processing via POST request."""
#     if request.method == "POST":
#         uploaded_file = request.FILES.get("document")

#         if not uploaded_file:
#             return JsonResponse({"error": "No document uploaded"}, status=400)

#         try:
#             # Validate file format
#             allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
#             if uploaded_file.content_type not in allowed_types:
#                 return JsonResponse({"error": "Invalid file format. Allowed: JPG, PNG, PDF"}, status=400)

#             # Extract text
#             extracted_text = extract_text(uploaded_file, uploaded_file.content_type)

#             # Classify document
#             document_type, confidence_score = classify_document(extracted_text)

#             # Extract entities
#             named_entities = extract_named_entities(extracted_text)

#             return JsonResponse({
#                 "message": "Processed successfully",
#                 "extracted_text": extracted_text,
#                 "document_type": document_type,
#                 "confidence_score": confidence_score,
#                 "named_entities": named_entities
#             }, status=200)

#         except Exception as e:
#             logging.error(f"Processing error: {traceback.format_exc()}")
#             return JsonResponse({"error": "Internal server error"}, status=500)

#     return JsonResponse({"error": "Only POST requests allowed"}, status=405)
