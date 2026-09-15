import urllib.parse
from django.utils.deprecation import MiddlewareMixin

class UTMTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to capture and persist UTM parameters and marketing attribution.
    Saves UTM parameters to session so they are not lost when the user navigates
    between multiple pages before submitting an enquiry.
    """

    UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']

    def process_request(self, request):
        # Retrieve existing data from session or initialize empty dictionary
        utm_data = request.session.get('utm_params', {})

        # Check if any new UTM parameter is present in current GET request
        has_new_utm = any(request.GET.get(key) for key in self.UTM_KEYS)

        if has_new_utm:
            for key in self.UTM_KEYS:
                val = request.GET.get(key)
                if val:
                    utm_data[key] = val.strip()

        # Check for general 'source' query parameter (e.g. ?source=facebook)
        if request.GET.get('source'):
            utm_data['source'] = request.GET.get('source').strip().capitalize()

        # Capture referrer if not already captured
        referrer = request.META.get('HTTP_REFERER', '')
        if referrer and 'referrer' not in utm_data:
            utm_data['referrer'] = referrer[:500]

        # Determine general source if not explicitly set
        if 'source' not in utm_data:
            utm_source = utm_data.get('utm_source', '').lower()
            ref_lower = referrer.lower()

            if 'google' in utm_source or 'google.' in ref_lower:
                utm_data['source'] = 'Google'
            elif 'facebook' in utm_source or 'fb' in utm_source or 'facebook.com' in ref_lower:
                utm_data['source'] = 'Facebook'
            elif 'instagram' in utm_source or 'instagram.com' in ref_lower:
                utm_data['source'] = 'Instagram'
            elif 'whatsapp' in utm_source or 'wa.me' in ref_lower:
                utm_data['source'] = 'WhatsApp'
            elif 'ad' in utm_source or 'cpc' in utm_data.get('utm_medium', '').lower():
                utm_data['source'] = 'Advertisement'
            elif not referrer:
                utm_data['source'] = 'Direct'
            else:
                utm_data['source'] = 'Website'

        # Persist back to session
        request.session['utm_params'] = utm_data
        request.session.modified = True

        # Attach convenience property to request
        request.utm_data = utm_data
