# adminpanel/helpers/email_branding.py

def get_email_branding(crm_id: str):
    """
    Returns logo_url and company_name based on the given CRM ID.
    Used for email templates across all modules.
    """

    BRANDING = {
        # --- Ascencia (first two CRM IDs) ---
        "771809603": {
            "logo_url": "https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png",
            "company_name": "Ascencia Malta"
        },
        "771661420": {
            "logo_url": "https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png",
            "company_name": "Ascencia Malta"
        },

        # --- College De Paris (CDP India / ) ---
        "755071407": {
            "logo_url": "https://dev.ascencia-interview.com/static/img/email_template_icon/cdp_india_logo.png",
            "company_name": "College De Paris"
        },
        "759439531": { #Intl
            "logo_url": "https://dev.ascencia-interview.com/static/img/email_template_icon/cdp_india_logo.png",
            "company_name": "College De Paris"
        }
    }

    # Default fallback (in case CRM ID not matched)
    DEFAULT_BRANDING = {
        "logo_url": "https://ascencia-interview.com/static/img/email_template_icon/ascencia_logo.png",
        "company_name": "Ascencia Malta"
    }

    branding = BRANDING.get(str(crm_id), DEFAULT_BRANDING)
    return branding["logo_url"], branding["company_name"]
