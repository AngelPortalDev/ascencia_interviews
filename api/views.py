from rest_framework.decorators import api_view
from rest_framework.response import Response
import pytesseract
import cv2
import numpy as np
import re
from pdf2image import convert_from_bytes
from PIL import Image
import io

MINDEE_API_KEY = "5312ebf992f9be224e442e5f72dbf389"


# @api_view(['POST'])
# def process_lead(request):
#     """Process the lead by validating the passport document"""
    
#     # Ensure the passport file is present
#     if 'document' not in request.FILES:
#         return Response({"error": "Passport file is required."}, status=400)

#     # Get the passport file from the request
#     passport_file = request.FILES.get('document')

#     # Check if the file type is supported
#     if passport_file.content_type not in ['application/pdf', 'image/jpeg', 'image/png']:
#         return Response({"error": "Unsupported file type."}, status=400)

#     # Step 1: Validate documents with Mindee
#     try:
#         mindee_response = validate_documents(passport_file)

#         # Check if the response contains valid data
#         if mindee_response.get('valid', False):
#             return Response({"message": "Lead successfully validated", "data": mindee_response}, status=200)
#         else:
#             return Response({"error": "Invalid document", "details": mindee_response}, status=400)

#     except Exception as e:
#         return Response({"error": f"Error validating document: {str(e)}"}, status=500)



# def validate_documents(passport):
#     url = "https://api.mindee.net/v1/products/mindee/passport/v1/predict"
#     headers = {"Authorization": f"Token {MINDEE_API_KEY}"}

#     with passport.open('rb') as file:
#         files = {"document": file}
#         try:
#             response = requests.post(url, headers=headers, files=files, timeout=30)  # Added timeout
#             response.raise_for_status()

#             result = response.json()
            
#             passport_no = result.get('document', {}).get('inference', {}).get('prediction', {}).get('id_number', {}).get('value')
#             id_confidence = result.get('document', {}).get('inference', {}).get('prediction', {}).get('id_number', {}).get('confidence')

#             # Validate passport number and confidence
#             if passport_no and id_confidence == 1:
#                 return {"valid": True, "details": result}
#             else:
#                 return {"valid": False}


#         except requests.exceptions.RequestException as e:
#             return {"valid": False, "error": f"Error validating document: {str(e)}"}

#         except Exception as e:
#             return {"valid": False, "error": f"Unexpected error: {str(e)}"}


     