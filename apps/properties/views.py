from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Property, Location, Amenity
from apps.advertisements.models import Advertisement
from apps.enquiries.forms import PropertyEnquiryForm
from apps.enquiries.services import build_whatsapp_chat_url

def property_list_view(request):
    """
    Searchable, filterable property catalog with pagination.
    Supports filters:
    - city, area, bhk, property_type, min_rent, max_rent, furnishing, availability
    """
    queryset = Property.objects.filter(status='available').select_related('location').prefetch_related('images', 'amenities')

    # Keyword Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(city__icontains=q) |
            Q(area__icontains=q) |
            Q(address__icontains=q)
        )

    # City filter
    city = request.GET.get('city', '').strip()
    if city:
        queryset = queryset.filter(city__iexact=city)

    # Area filter
    area = request.GET.get('area', '').strip()
    if area:
        queryset = queryset.filter(area__icontains=area)

    # BHK filter
    bhk = request.GET.get('bhk', '').strip()
    if bhk:
        queryset = queryset.filter(bhk=bhk)

    # Property Type filter
    property_type = request.GET.get('property_type', '').strip()
    if property_type:
        queryset = queryset.filter(property_type=property_type)

    # Furnishing filter
    furnishing = request.GET.get('furnishing', '').strip()
    if furnishing:
        queryset = queryset.filter(furnishing=furnishing)

    # Min Rent
    min_rent = request.GET.get('min_rent', '').strip()
    if min_rent and min_rent.isdigit():
        queryset = queryset.filter(rent__gte=int(min_rent))

    # Max Rent
    max_rent = request.GET.get('max_rent', '').strip()
    if max_rent and max_rent.isdigit():
        queryset = queryset.filter(rent__lte=int(max_rent))

    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'rent_asc':
        queryset = queryset.order_by('rent')
    elif sort_by == 'rent_desc':
        queryset = queryset.order_by('-rent')
    elif sort_by == 'newest':
        queryset = queryset.order_by('-created_at')
    else:  # 'featured' default
        queryset = queryset.order_by('-is_featured', '-created_at')

    # Available cities for filter dropdown
    available_cities = Property.objects.filter(status='available').values_list('city', flat=True).distinct().order_by('city')

    # Active advertisement for property listing
    listing_ad = Advertisement.get_active_ad(placement='property_listing')

    # Pagination: 9 properties per page
    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page', 1)
    try:
        properties_page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        properties_page = paginator.page(1)

    # Construct query string without page parameter for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    context = {
        'properties': properties_page,
        'total_count': paginator.count,
        'available_cities': available_cities,
        'bhk_choices': Property.BHK_CHOICES,
        'property_types': Property.PROPERTY_TYPE_CHOICES,
        'furnishing_choices': Property.FURNISHING_CHOICES,
        'selected_city': city,
        'selected_area': area,
        'selected_bhk': bhk,
        'selected_type': property_type,
        'selected_furnishing': furnishing,
        'selected_min_rent': min_rent,
        'selected_max_rent': max_rent,
        'selected_sort': sort_by,
        'search_query': q,
        'querystring': querystring,
        'listing_ad': listing_ad,
        'meta_title': f"Rental Properties & Verified Flats | Rentorra",
        'meta_description': f"Browse {paginator.count} verified rental flats, apartments, and houses across top locations. Filter by BHK, budget, and furnishing.",
    }
    return render(request, 'properties/list.html', context)


def property_detail_view(request, slug):
    """
    Detailed property view:
    - High-res image gallery
    - Key specifications and amenities
    - WhatsApp click-to-chat with pre-filled message
    - Phone call link
    - Property-specific enquiry form
    - Similar property recommendations
    - Sticky mobile action bar
    """
    property_obj = get_object_or_404(
        Property.objects.select_related('location').prefetch_related('images', 'amenities'),
        slug=slug
    )

    # Fetch similar properties in same city or same BHK
    similar_properties = Property.objects.filter(
        status='available',
        city__iexact=property_obj.city
    ).exclude(pk=property_obj.pk).prefetch_related('images')[:3]

    # Pre-filled WhatsApp link
    whatsapp_message = (
        f"Hello Rentorra, I am interested in renting '{property_obj.title}' "
        f"({property_obj.get_bhk_display()}, {property_obj.area}, {property_obj.city}) "
        f"listed at {property_obj.formatted_rent}/month. Please share more details."
    )
    whatsapp_url = build_whatsapp_chat_url(whatsapp_message)

    # Property-specific enquiry form instance
    initial_data = {
        'property': property_obj.pk,
        'city': property_obj.city,
        'bhk': property_obj.bhk,
        'property_type': property_obj.property_type,
        'min_budget': property_obj.rent,
        'max_budget': property_obj.rent,
    }
    enquiry_form = PropertyEnquiryForm(initial=initial_data)

    # Active advertisement for property detail sidebar
    detail_ad = Advertisement.get_active_ad(placement='property_detail')

    context = {
        'property': property_obj,
        'images': property_obj.images.all(),
        'amenities': property_obj.amenities.all(),
        'similar_properties': similar_properties,
        'whatsapp_url': whatsapp_url,
        'enquiry_form': enquiry_form,
        'detail_ad': detail_ad,
        'meta_title': property_obj.meta_title or f"{property_obj.title} | Rentorra",
        'meta_description': property_obj.meta_description or f"Rent this {property_obj.get_bhk_display()} in {property_obj.area}, {property_obj.city} for {property_obj.formatted_rent}/month. Zero hassle, verified home.",
    }
    return render(request, 'properties/detail.html', context)


def location_landing_view(request, slug):
    """
    Dynamic SEO landing page for specific cities or micro-markets.
    Example: /properties/location/noida/ or /properties/location/sector-62-noida/
    """
    location = get_object_or_404(Location, slug=slug, is_active=True)
    properties = Property.objects.filter(
        status='available',
        city__iexact=location.city
    ).filter(
        Q(area__iexact=location.area) | Q(location=location)
    ).select_related('location').prefetch_related('images')

    paginator = Paginator(properties, 9)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'location': location,
        'properties': page_obj,
        'total_count': paginator.count,
        'meta_title': location.meta_title or f"Flats & Apartments for Rent in {location.area}, {location.city} | Rentorra",
        'meta_description': location.meta_description or f"Explore verified 1, 2, 3 BHK flats for rent in {location.area}, {location.city}. Direct specialist assistance, zero hassle.",
    }
    return render(request, 'properties/location_landing.html', context)
