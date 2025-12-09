from django.conf import settings
import logging
from django.core.mail import EmailMultiAlternatives
logger = logging.getLogger(__name__)  # Logger for error tracking

def send_email(subject, message, recipient=None, cc=None, reply_to=None):
    recipient = recipient or []  # Ensure recipient is a list
    cc = cc or []  # Ensure cc is a list


    # Add global CC from settings (auto applied everywhere)
    if hasattr(settings, "DEFAULT_CC_EMAILS"):
        cc = list(set(cc + settings.DEFAULT_CC_EMAILS))

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient,
            cc=cc,
            reply_to=reply_to
        )
        # email.content_subtype = "html"  # Set email format to HTML
        email.attach_alternative(message, "text/html")  # Correct way
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")  # Log the error
        return False
