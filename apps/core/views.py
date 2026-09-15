import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from .forms import ContactForm
from .models import ContactMessage
from apps.properties.models import Property, Location
from apps.advertisements.models import Advertisement

logger = logging.getLogger('apps.core')

def home_view(request):
    """
    Rentorra Homepage:
    - Hero section with quick requirement search
    - Featured rental properties
    - Popular locations
    - Why Choose Rentorra & How it Works
    - Active homepage advertisements
    """
    featured_properties = Property.objects.filter(
        status='available', is_featured=True
    ).select_related('location').prefetch_related('images', 'amenities')[:6]

    recent_properties = Property.objects.filter(
        status='available'
    ).select_related('location').prefetch_related('images')[:8]

    popular_locations = Location.objects.filter(is_active=True)[:8]

    # Active Advertisements for homepage hero/banner
    hero_ad = Advertisement.get_active_ad(placement='homepage_hero')
    banner_ad = Advertisement.get_active_ad(placement='homepage_banner')

    # Quick count of available properties
    available_count = Property.objects.filter(status='available').count()

    available_cities = Property.objects.filter(status='available').values_list('city', flat=True).distinct().order_by('city')

    context = {
        'featured_properties': featured_properties,
        'recent_properties': recent_properties,
        'popular_locations': popular_locations,
        'hero_ad': hero_ad,
        'banner_ad': banner_ad,
        'available_count': available_count,
        'available_cities': available_cities,
        'bhk_choices': Property.BHK_CHOICES,
        'property_types': Property.PROPERTY_TYPE_CHOICES,
        'meta_title': 'Rentorra - Find Your Perfect Rental Home | Verified Flats & Apartments',
        'meta_description': 'Discover verified 1, 2, 3, 4 BHK rental flats, apartments, and independent homes with zero brokerage hassle. Contact Rentorra property experts today.',
    }
    return render(request, 'home.html', context)

def about_view(request):
    """About Rentorra: Mission, Vision, and Trust signals."""
    context = {
        'meta_title': 'About Us - Rentorra Rental Property Specialists',
        'meta_description': 'Learn how Rentorra makes renting hassle-free with verified listings, direct support, and tailored home discovery.',
    }
    return render(request, 'pages/about.html', context)

def contact_view(request):
    """Contact Rentorra: Office details, phone, WhatsApp and enquiry message form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save(commit=False)
            contact_msg.ip_address = request.META.get('REMOTE_ADDR')
            contact_msg.save()
            logger.info("New contact message received from %s (%s)", contact_msg.name, contact_msg.phone)
            messages.success(request, "Thank you for reaching out! Our property specialist will contact you shortly.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = ContactForm()

    context = {
        'form': form,
        'meta_title': 'Contact Rentorra - Call, WhatsApp or Message Us',
        'meta_description': 'Get in touch with Rentorra. Speak directly with a rental housing expert in Noida, Gurugram, Bengaluru, and major metro hubs.',
    }
    return render(request, 'pages/contact.html', context)

def privacy_view(request):
    """Privacy Policy page."""
    return render(request, 'pages/privacy.html', {
        'meta_title': 'Privacy Policy - Rentorra',
    })

def terms_view(request):
    """Terms & Conditions page."""
    return render(request, 'pages/terms.html', {
        'meta_title': 'Terms & Conditions - Rentorra',
    })

def robots_txt_view(request):
    """Generate dynamic robots.txt."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /enquiries/success/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def custom_404_view(request, exception=None):
    """Custom branded 404 error handler."""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """Custom branded 500 error handler."""
    return render(request, '500.html', status=500)
