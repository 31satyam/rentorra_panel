import logging
import urllib.parse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger('apps.enquiries')

def build_whatsapp_chat_url(message, phone_number=None):
    """
    Generates a wa.me URL with pre-filled message text.
    If phone_number is not provided, defaults to configured company WhatsApp number.
    """
    if not phone_number:
        raw_number = getattr(settings, 'WHATSAPP_NUMBER', '+919876543210')
        phone_number = ''.join(c for c in raw_number if c.isdigit())
        if phone_number.startswith('0'):
            phone_number = '91' + phone_number[1:]
        elif len(phone_number) == 10:
            phone_number = '91' + phone_number

    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_msg}"


def build_lead_followup_whatsapp_url(enquiry):
    """
    Constructs a WhatsApp outreach link for sales agents to message the customer directly.
    """
    customer_phone = enquiry.clean_whatsapp
    if not customer_phone:
        return ""
    
    greeting = f"Hello {enquiry.name}, thank you for contacting Rentorra regarding rental homes in {enquiry.city}."
    if enquiry.property:
        greeting = f"Hello {enquiry.name}, thank you for your interest in '{enquiry.property.title}' on Rentorra."

    encoded_msg = urllib.parse.quote(f"{greeting} How may our rental advisor assist your move-in?")
    return f"https://wa.me/{customer_phone}?text={encoded_msg}"


def send_enquiry_notification_email(enquiry):
    """
    Dispatches a structured email notification to the sales team / ADMIN_EMAIL.
    Logs success or failures gracefully so user submission is never interrupted.
    """
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'sales@rentorra.com')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Rentorra Leads <leads@rentorra.com>')

    subject = f"[New Lead] {enquiry.name} - {enquiry.bhk or 'Property Enquiry'} in {enquiry.city}"
    
    target_item = enquiry.property.title if enquiry.property else f"{enquiry.bhk} in {enquiry.preferred_area or enquiry.city}"

    context = {
        'enquiry': enquiry,
        'target_item': target_item,
        'company_name': getattr(settings, 'COMPANY_NAME', 'Rentorra'),
    }

    try:
        html_message = render_to_string('enquiries/emails/admin_alert.html', context)
        plain_message = f"""
New Rental Lead Received on Rentorra!

Lead Details:
- Name: {enquiry.name}
- Phone: {enquiry.phone}
- Email: {enquiry.email or 'N/A'}
- City: {enquiry.city}
- Preferred Area: {enquiry.preferred_area or 'N/A'}
- Requirement: {target_item}
- Budget: ₹{enquiry.min_budget or 0:,} - ₹{enquiry.max_budget or 0:,}
- Source: {enquiry.source} (Campaign: {enquiry.utm_campaign or 'N/A'})
- Message: {enquiry.message or 'N/A'}

Login to the Rentorra Admin to assign or contact this lead:
Status: {enquiry.get_status_display()}
"""
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=True,
        )
        logger.info("Enquiry email notification sent for enquiry ID #%s to %s", enquiry.pk, admin_email)
        return True
    except Exception as exc:
        logger.warning("Failed to send enquiry email notification for #%s: %s", enquiry.pk, exc)
        return False
