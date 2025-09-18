import logging
from django.utils.timezone import now
from django.db.models import Case, When, Value, IntegerField
from studentpanel.models.interview_link import StudentInterviewLink
import requests
from studentpanel.utils.ZohoAuth import ZohoAuth

logger = logging.getLogger(__name__)

def update_expired_links_in_zoho():
    print("trigger expired status")
    logger.info("🔔 Checking for expired interview links...")

    # ✅ Annotate links with priority: Mg== (2) > MQ== (1) > others (0)
    links = (
        StudentInterviewLink.objects.annotate(
            link_priority=Case(
                When(interview_link_count="Mg==", then=Value(2)),
                When(interview_link_count="MQ==", then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .order_by("zoho_lead_id", "-link_priority", "-id")
    )

    if not links.exists():
        logger.info("✅ No interview links found.")
        return "No links"

    # ✅ Group by zoho_lead_id and pick highest priority link
    lead_latest_links = {}
    for link in links:
        if link.zoho_lead_id not in lead_latest_links:
            lead_latest_links[link.zoho_lead_id] = link
            logger.info(
                f"🔎 Selected link for Lead {link.zoho_lead_id}: "
                f"{link.interview_link_count} (priority={link.link_priority}, id={link.id})"
            )

    auth = ZohoAuth()
    updated_count = 0

    for zoho_lead_id, link in lead_latest_links.items():
        crm_id = str(link.crm_id) if hasattr(link, "crm_id") else "771809603"

        # ✅ Determine Interview Status based on chosen link
        if link.interview_attend:
            status = "Interview Done"
        elif link.expires_at and link.expires_at < now():
            status = "Expired"
        elif link.interview_link_count == "Mg==":
            status = "Second Link Active"
        elif link.interview_link_count == "MQ==":
            status = "First Link Active"
        else:
            status = "Pending"

        try:
            access_token = auth.get_access_token(crm_id)

            url = "https://www.zohoapis.com/crm/v2/Leads"
            headers = {
                "Authorization": f"Zoho-oauthtoken {access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "data": [
                    {"id": zoho_lead_id, "Interview_Status": status}
                ]
            }

            response = requests.put(url, json=payload, headers=headers)

            if response.status_code in (200, 202):
                updated_count += 1
                logger.info(
                    f"✅ Zoho Lead {zoho_lead_id} status updated to '{status}' "
                    f"(Link ID {link.id}, Priority {link.link_priority})."
                )
            else:
                logger.error(
                    f"❌ Failed to update Zoho Lead {zoho_lead_id}: {response.text}"
                )

        except Exception as e:
            logger.exception(f"🔥 Error updating Zoho Lead {zoho_lead_id}: {e}")

    logger.info(f"🎯 Zoho update completed. Total leads updated: {updated_count}")
    return f"Updated {updated_count} Zoho leads"
