from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from apps.properties.models import Property
from apps.enquiries.models import Enquiry
from apps.enquiries.services import build_lead_followup_whatsapp_url
from apps.advertisements.models import Advertisement

@staff_member_required
def dashboard_view(request):
    """
    Internal Sales & Marketing Team Dashboard:
    - Business KPIs
    - Conversion Pipeline Status
    - Lead Source Attribution Breakdown
    - Quick Action Leads Table (Call, WhatsApp, Email, Status change)
    """
    if request.method == 'POST' and 'update_status' in request.POST:
        enquiry_id = request.POST.get('enquiry_id')
        new_status = request.POST.get('new_status')
        remark = request.POST.get('admin_remark', '').strip()
        enquiry = get_object_or_404(Enquiry, pk=enquiry_id)
        enquiry.status = new_status
        if remark:
            enquiry.admin_remark = f"{enquiry.admin_remark}\n[{request.user.username}]: {remark}".strip()
        enquiry.save()
        messages.success(request, f"Lead #{enquiry.id} status updated to {enquiry.get_status_display()}.")
        return redirect('staff_dashboard')

    # Property KPIs
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(status='available').count()
    rented_properties = Property.objects.filter(status='rented').count()
    featured_properties = Property.objects.filter(is_featured=True).count()

    # Enquiry & Pipeline KPIs
    total_enquiries = Enquiry.objects.count()
    new_enquiries = Enquiry.objects.filter(status='new').count()
    contacted_leads = Enquiry.objects.filter(status='contacted').count()
    interested_leads = Enquiry.objects.filter(status='interested').count()
    visits_scheduled = Enquiry.objects.filter(status='visit_scheduled').count()
    converted_leads = Enquiry.objects.filter(status='converted').count()

    # Lead Sources Breakdown
    sources_data = Enquiry.objects.values('source').annotate(count=Count('id')).order_by('-count')
    total_with_source = sum(item['count'] for item in sources_data) or 1
    lead_sources = [
        {
            'name': item['source'] or 'Direct / Unknown',
            'count': item['count'],
            'percentage': round((item['count'] / total_with_source) * 100, 1)
        }
        for item in sources_data
    ]

    # Recent Enquiries (Latest 15)
    recent_enquiries_qs = Enquiry.objects.select_related('property', 'assigned_to').order_by('-created_at')[:15]
    
    # Attach WhatsApp outreach URL to each enquiry
    recent_enquiries = []
    for enq in recent_enquiries_qs:
        enq.wa_url = build_lead_followup_whatsapp_url(enq)
        recent_enquiries.append(enq)

    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'featured_properties': featured_properties,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'contacted_leads': contacted_leads,
        'interested_leads': interested_leads,
        'visits_scheduled': visits_scheduled,
        'converted_leads': converted_leads,
        'lead_sources': lead_sources,
        'recent_enquiries': recent_enquiries,
        'status_choices': Enquiry.STATUS_CHOICES,
        'meta_title': 'Rentorra Sales & Lead Dashboard',
    }
    return render(request, 'accounts/dashboard.html', context)
