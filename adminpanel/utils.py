from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)  # Logger for error tracking

def send_email(subject, message, recipient=None, cc=None):
    recipient = recipient or []  # Ensure recipient is a list
    cc = cc or []  # Ensure cc is a list

    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient,
            cc=cc,
        )
        email.content_subtype = "html"  # Set email format to HTML
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")  # Log the error
        return False
