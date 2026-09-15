import logging
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Advertisement, AdvertisementClick

logger = logging.getLogger('apps.advertisements')

def ad_click_redirect_view(request, ad_id):
    """
    Tracks an advertisement click and redirects the visitor to the destination.
    Preserves and injects campaign attribution.
    """
    ad = get_object_or_404(Advertisement, pk=ad_id)

    # Record click
    try:
        AdvertisementClick.objects.create(
            advertisement=ad,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referrer=request.META.get('HTTP_REFERER', '')[:500]
        )
        logger.info("Ad click recorded for ad #%s: %s", ad.pk, ad.title)
    except Exception as exc:
        logger.warning("Failed to record ad click for #%s: %s", ad.pk, exc)

    destination = ad.destination_url

    # If destination is internal property, attach UTM for campaign continuity
    if ad.property:
        separator = '&' if '?' in destination else '?'
        destination = f"{destination}{separator}utm_source=Rentorra&utm_medium=internal_ad&utm_campaign=banner_{ad.pk}"

    return HttpResponseRedirect(destination)
