# helpers.py

from django.core.exceptions import ValidationError
import base64
def save_data(modelInstance, data, where=None):
    try:
        # If 'where' condition is provided, check for existing data
        if where:
            exists = modelInstance.objects.filter(**where).first()
            if exists:
                # Update the existing record
                for key, value in data.items():
                    setattr(exists, key, value)
                exists.save()
                return {'status': True, 'id': exists.id}
            else:
                # Create new record if it doesn't exist
                new_instance = modelInstance.objects.create(**data)
                return {'status': True, 'id': new_instance.id}
        else:
            # No condition, create new instance
            new_instance = modelInstance.objects.create(**data)
            return {'status': True, 'id': new_instance.id}
    except Exception as e:
        return {'status': False, 'error': str(e)}

def base64_encode(id_value):
    """Encodes the ID to base64."""
    return base64.urlsafe_b64encode(str(id_value).encode()).decode()

# Function to decode a base64 encoded ID
def base64_decode(encoded_value):
    """Decodes the base64 encoded ID."""
    try:
        decoded_value = base64.urlsafe_b64decode(encoded_value.encode()).decode()
        return decoded_value
    except Exception:
        return None