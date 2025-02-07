import tempfile
import base64
import mimetypes
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rapidfuzz import fuzz
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from mindee import Client, AsyncPredictResponse, product


# Initialize Mindee client
mindee_client = Client(api_key="4951866b395bb3fefdb1e4753c6bbd8e")

# Add endpoint configuration
my_endpoint = mindee_client.create_endpoint(
    account_name="ANKITAGAVAS",
    endpoint_name="eductional_cert_v4",
    version="1"
)


# Define educational certificate keywords
EDUCATION_CERTIFICATE_KEYWORDS = [
    "Certificate of Completion", "Degree", "Diploma", "Bachelor", "Master",
    "Doctorate", "University", "College", "Institution", "High School",
    "Transcript", "Graduation", "Awarded", "Academic", "Educational",
    "Associate Degree", "Graduate Degree", "Postgraduate Degree", "Professional Degree",
    "Honorary Degree", "Juris Doctor", "PhD", "MD", "MBA", "MS", "MA", "BSc", "BA",
    "Vocational Certificate", "Technical Diploma", "Online Certification", "Distance Learning",
    "Course Completion", "Credential", "Accreditation", "Qualification", "Specialization",
    "Major", "Minor", "Field of Study", "Thesis", "Dissertation", "Research Paper",
    "Academic Record", "Grade Sheet", "Mark Sheet", "Enrollment Verification", "Degree Verification",
    "Proof of Education", "Educational Attainment", "Alumni", "Commencement", "Convocation"
]

RESTRICTED_FILE_NAMES = ["passport", "cv", "resume"]
FUZZY_THRESHOLD = 85  # Adjust threshold for stricter/looser matching

def serialize_field(field):
    """Recursively serializes fields into JSON serializable formats."""
    if isinstance(field, dict):  # If already a dictionary
        return {key: serialize_field(value) for key, value in field.items()}
    elif isinstance(field, list):  # If it's a list, process each element
        return [serialize_field(item) for item in field]
    else:
        return str(field) if field is not None else "N/A"

def is_restricted_filename(filename):
    filename = filename.lower()  # Normalize to lowercase
    
    for restricted_word in RESTRICTED_FILE_NAMES:
        similarity_score = fuzz.partial_ratio(restricted_word, filename)
        
        if similarity_score >= FUZZY_THRESHOLD:
            return True  # Block file if it matches closely
    
    return False

# OCR Preprocessing: Noise Reduction & Adaptive Thresholding
def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply adaptive thresholding
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 31, 2)
    
    # Optional: Apply noise reduction
    kernel = np.ones((1, 1), np.uint8)
    threshold = cv2.dilate(threshold, kernel, iterations=1)
    threshold = cv2.erode(threshold, kernel, iterations=1)
    
    return threshold

# Extract text using optimized OCR settings
def extract_text_from_image(image):
    processed_image = preprocess_image(image)
    text = pytesseract.image_to_string(processed_image, config='--psm 6 --oem 3')
    return text.strip()

# Convert PDF pages to images & extract text in parallel
def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    extracted_text = ""

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        texts = list(executor.map(extract_text_from_image, images))
        extracted_text = " ".join(texts).strip()

    return extracted_text if extracted_text else ""

# Extract text from an image file (PNG, JPG, JPEG)
def extract_text_from_image_file(image_path):
    image = Image.open(image_path)
    return extract_text_from_image(image)

# Keyword Matching with Fuzzy Search (Better Accuracy)
def check_educational_keywords(text):
    threshold = 90  # Adjust this to reduce false positives
    matched_keywords = []

    for keyword in EDUCATION_CERTIFICATE_KEYWORDS:
        score = fuzz.partial_ratio(keyword.lower(), text.lower())
        if score > threshold:
            matched_keywords.append(keyword)

    # Require at least 3 distinct educational keywords to classify as an educational certificate
    return len(set(matched_keywords)) >= 5


def is_certificate_filename(filename):
    certificate_keywords = [
        "certificate", "diploma", "degree", "transcript",  
        "completion", "training", "achievement", "award", "merit",  
        "qualification", "course", "certification", "graduate",  
        "honors", "recognition", "accreditation", "licensure",  
        "appreciation", "scholarship", "education", "proficiency",  
        "competency", "accomplishment", "exam", "assessment",  
        "school", "university", "college", "institution", "faculty"
    ]

    return any(keyword in filename for keyword in certificate_keywords)


@csrf_exempt
def process_document(request):
    if request.method == "POST":
        try:
            # Check if a file was uploaded
            uploaded_file = request.FILES.get("document")
            if not uploaded_file:
                return JsonResponse({"error": "No document uploaded"}, status=400)

            # Check for restricted filenames
            filename = uploaded_file.name.lower()
            if is_restricted_filename(filename):
                return JsonResponse({"error": "Invalid file. Passport, CV, and Resume files are not allowed."}, status=400)

            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # Validate file type
            mime_type = uploaded_file.content_type
            if mime_type not in ["application/pdf", "image/png", "image/jpeg", "image/jpg"]:
                return JsonResponse({"error": "Invalid file type. Only PDF, PNG, JPG, and JPEG files are supported."}, status=400)

            # Extract text based on file type
            try:
                if mime_type == "application/pdf":
                    extracted_text = extract_text_from_pdf(temp_file_path)
                else:
                    extracted_text = extract_text_from_image_file(temp_file_path)

                if not extracted_text:
                    return JsonResponse({"error": "Text extraction failed. The document might be too blurry or contain no text."}, status=400)
            except Exception as e:
                return JsonResponse({"error": f"Text extraction failed: {str(e)}"}, status=500)

            # Check for educational certificate keywords
            contains_edu_keywords = check_educational_keywords(extracted_text)

            if contains_edu_keywords or is_certificate_filename(filename):  
                try:
                    # Validate MIME type again (redundant but ensures safety)
                    mime_type, _ = mimetypes.guess_type(temp_file_path)
                    if mime_type != 'application/pdf':
                        return JsonResponse({"error": "Invalid file type. Only PDF files are supported."}, status=400)

                    # Create document source
                    input_doc = mindee_client.source_from_path(temp_file_path)

                    # Process document asynchronously
                    result: AsyncPredictResponse = mindee_client.enqueue_and_parse(
                        product.GeneratedV1,  
                        input_doc,
                        endpoint=my_endpoint
                    )

                    # Access the parsed document data
                    prediction = result.document.inference.prediction

                    # Convert to dictionary before serialization
                    serialized_prediction = serialize_field(vars(prediction))

                    # Return success response
                    return JsonResponse({
                        "message": "Success",
                        "prediction": serialized_prediction,
                    }, status=200)
                except Exception as e:
                    return JsonResponse({"error": f"Mindee API processing failed: {str(e)}"}, status=500)
            else:
                return JsonResponse({
                    "message": "Error",
                    "is_education_certificate": False,
                }, status=200)

        except Exception as e:
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)



    