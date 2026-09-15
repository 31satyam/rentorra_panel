from django.conf import settings
from datetime import datetime

def rentorra_settings(request):
    """
    Exposes brand and contact configurations to all templates.
    """
    # Clean phone numbers for tel: and wa.me links
    raw_phone = getattr(settings, 'COMPANY_PHONE', '+919876543210')
    clean_phone = ''.join(c for c in raw_phone if c.isdigit() or c == '+')
    
    raw_whatsapp = getattr(settings, 'WHATSAPP_NUMBER', '+919876543210')
    clean_whatsapp = ''.join(c for c in raw_whatsapp if c.isdigit())
    # If starting with +, wa.me does not need the +
    if clean_whatsapp.startswith('+'):
        clean_whatsapp = clean_whatsapp[1:]

    return {
        'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'Rentorra'),
        'COMPANY_TAGLINE': getattr(settings, 'COMPANY_TAGLINE', 'Find Your Perfect Rental Home'),
        'COMPANY_PHONE': raw_phone,
        'COMPANY_PHONE_TEL': clean_phone,
        'COMPANY_EMAIL': getattr(settings, 'COMPANY_EMAIL', 'contact@rentorra.com'),
        'COMPANY_ADDRESS': getattr(settings, 'COMPANY_ADDRESS', 'Plot 45, Sector 62, Noida, Uttar Pradesh 201309'),
        'WHATSAPP_NUMBER': raw_whatsapp,
        'WHATSAPP_LINK_NUMBER': clean_whatsapp,
        'CURRENT_YEAR': datetime.now().year,
        'UTM_DATA': getattr(request, 'utm_data', {}),
    }
