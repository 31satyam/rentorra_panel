import logging
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Enquiry
from .forms import PropertyEnquiryForm, FindPropertyForm
from .services import send_enquiry_notification_email, build_whatsapp_chat_url
from apps.properties.models import Property

logger = logging.getLogger('apps.enquiries')

def populate_utm_fields(enquiry, request):
    """
    Helper to populate UTM and attribution data on an enquiry from the session/request.
    """
    utm_data = request.session.get('utm_params', {})
    
    enquiry.utm_source = utm_data.get('utm_source', '')[:150]
    enquiry.utm_medium = utm_data.get('utm_medium', '')[:150]
    enquiry.utm_campaign = utm_data.get('utm_campaign', '')[:200]
    enquiry.utm_term = utm_data.get('utm_term', '')[:200]
    enquiry.utm_content = utm_data.get('utm_content', '')[:200]
    enquiry.source = utm_data.get('source', 'Website')[:50]
    enquiry.ip_address = request.META.get('REMOTE_ADDR')
    enquiry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]


def is_duplicate_submission(phone, city, property_id=None):
    """
    Anti-spam duplicate submission protection: checks if an identical lead
    was posted within the last 5 minutes.
    """
    cutoff = timezone.now() - timedelta(minutes=5)
    qs = Enquiry.objects.filter(phone=phone, city=city, created_at__gte=cutoff)
    if property_id:
        qs = qs.filter(property_id=property_id)
    return qs.exists()


def property_enquiry_create_view(request):
    """
    Handles property-specific enquiry submissions from detail pages and modals.
    """
    if request.method != 'POST':
        return redirect('property_list')

    form = PropertyEnquiryForm(request.POST)
    if form.is_valid():
        phone = form.cleaned_data.get('phone')
        city = form.cleaned_data.get('city')
        prop = form.cleaned_data.get('property')

        # Check duplicate submission
        if is_duplicate_submission(phone, city, prop.id if prop else None):
            logger.info("Duplicate enquiry submission ignored for phone %s", phone)
            messages.info(request, "We have already received your enquiry. Our leasing advisor will call you shortly!")
            return redirect('enquiry_success')

        enquiry = form.save(commit=False)
        populate_utm_fields(enquiry, request)
        enquiry.save()

        # Trigger notification
        send_enquiry_notification_email(enquiry)

        # Store enquiry ID in session for personalized success page
        request.session['latest_enquiry_id'] = enquiry.id
        logger.info("New property enquiry #%s created from %s", enquiry.id, enquiry.source)
        return redirect('enquiry_success')
    else:
        # Form has errors - redirect back to property page if possible
        prop_id = request.POST.get('property')
        if prop_id:
            try:
                prop = Property.objects.get(pk=prop_id)
                messages.error(request, "Please check the entered mobile number and fields.")
                return redirect(prop.get_absolute_url())
            except Property.DoesNotExist:
                pass
        messages.error(request, "Please check the form for errors.")
        return redirect('property_list')


def find_property_view(request):
    """
    Dedicated /find-property/ intake page.

    - Pre-populates fields if search parameters are passed in GET query.
    - Validates and saves rental requirements.
    - Shows exact validation errors on the frontend.
    """

    if request.method == "POST":
        form = FindPropertyForm(request.POST)

        if form.is_valid():
            phone = form.cleaned_data.get("phone")
            city = form.cleaned_data.get("city")

            # Check duplicate submission
            if is_duplicate_submission(phone, city):
                logger.info(
                    "Duplicate requirement submission ignored for phone %s",
                    phone
                )

                messages.info(
                    request,
                    "We have already received your requirement. "
                    "Our leasing advisor is on it!"
                )

                return redirect("enquiry_success")

            # Create enquiry
            enquiry = form.save(commit=False)

            # Populate UTM/source information
            populate_utm_fields(enquiry, request)

            # Save
            enquiry.save()

            # Send notification
            send_enquiry_notification_email(enquiry)

            # Store latest enquiry
            request.session["latest_enquiry_id"] = enquiry.id

            logger.info(
                "New requirement enquiry #%s created via /find-property/ from %s",
                enquiry.id,
                enquiry.source,
            )

            messages.success(
                request,
                "Your rental requirement has been submitted successfully!"
            )

            return redirect("enquiry_success")

        else:
            # Log exact validation errors
            logger.warning(
                "Find Property form validation failed: %s",
                form.errors.as_json()
            )

            # Also log field-by-field errors
            for field_name, errors in form.errors.items():
                for error in errors:
                    logger.warning(
                        "Find Property validation error | field=%s | error=%s",
                        field_name,
                        error,
                    )

            # Generic message at top of page
            messages.error(
                request,
                "Please correct the errors highlighted below."
            )

    else:
        # Pre-populate from GET params if coming from search widgets
        initial = {}

        if request.GET.get("city"):
            initial["city"] = request.GET.get("city")

        if request.GET.get("bhk"):
            bhk_val = request.GET.get("bhk")

            # Map BHK choice to display value if necessary
            for val, label in Property.BHK_CHOICES:
                if val == bhk_val:
                    initial["bhk"] = label
                    break

        if request.GET.get("min_budget"):
            initial["min_budget"] = request.GET.get("min_budget")

        if request.GET.get("max_budget"):
            initial["max_budget"] = request.GET.get("max_budget")

        form = FindPropertyForm(initial=initial)

    context = {
        "form": form,
        "meta_title": (
            "Find a Rental Property - Submit Your Requirement | Rentorra"
        ),
        "meta_description": (
            "Looking for a flat, apartment or house for rent? "
            "Submit your budget and location preferences. "
            "Rentorra property specialists will find matched homes for you."
        ),
    }

    return render(
        request,
        "enquiries/find_property.html",
        context
    )


def enquiry_success_view(request):
    """
    Thank you and confirmation page after successful lead submission.
    Displays personalized message and optional one-click WhatsApp connect.
    """
    enquiry_id = request.session.get('latest_enquiry_id')
    enquiry = None
    whatsapp_url = None

    if enquiry_id:
        try:
            enquiry = Enquiry.objects.select_related('property').get(pk=enquiry_id)
            # Dynamic WhatsApp click-to-chat message
            target = enquiry.property.title if enquiry.property else f"{enquiry.bhk or 'Rental Home'} in {enquiry.city}"
            msg = f"Hello Rentorra, I just submitted an enquiry for {target}. My name is {enquiry.name}."
            whatsapp_url = build_whatsapp_chat_url(msg)
        except Enquiry.DoesNotExist:
            pass

    context = {
        'enquiry': enquiry,
        'whatsapp_url': whatsapp_url,
        'meta_title': 'Thank You - Requirement Received | Rentorra',
    }
    return render(request, 'enquiries/success.html', context)
