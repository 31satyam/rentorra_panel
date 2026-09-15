from django.contrib import admin
from django.utils.html import format_html
from .models import Enquiry
from .services import build_lead_followup_whatsapp_url

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'lead_name_contact',
        'requirement_summary',
        'city',
        'source_badge',
        'status',
        'assigned_to',
        'quick_actions',
        'created_at',
    )
    list_display_links = ('id', 'lead_name_contact')
    list_filter = (
        'status',
        'source',
        'city',
        'bhk',
        'created_at',
        'assigned_to',
        'preferred_contact_method',
    )
    search_fields = (
        'name',
        'phone',
        'email',
        'city',
        'preferred_area',
        'utm_campaign',
        'utm_source',
        'admin_remark',
    )
    list_editable = ('status', 'assigned_to')
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = (
        'created_at',
        'updated_at',
        'ip_address',
        'user_agent',
        'utm_source',
        'utm_medium',
        'utm_campaign',
        'utm_term',
        'utm_content',
        'source',
    )

    fieldsets = (
        ('Lead Information', {
            'fields': (
                'name', 'phone', 'email', 'whatsapp_number', 'preferred_contact_method'
            )
        }),
        ('Requirement Details', {
            'fields': (
                'property', 'looking_for', 'property_type', 'bhk', 'city', 'preferred_area',
                'min_budget', 'max_budget', 'furnishing', 'move_in_date', 'message'
            )
        }),
        ('Sales Pipeline & CRM', {
            'fields': (
                'status', 'assigned_to', 'admin_remark'
            )
        }),
        ('Marketing & Attribution (UTM)', {
            'classes': ('collapse',),
            'fields': (
                'source', 'utm_source', 'utm_medium', 'utm_campaign',
                'utm_term', 'utm_content', 'ip_address', 'user_agent'
            )
        }),
        ('Audit Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )

    def lead_name_contact(self, obj):
        return format_html(
            '<strong>{}</strong><br><small class="text-muted"><i class="bi bi-telephone"></i> {}</small>',
            obj.name, obj.phone
        )
    lead_name_contact.short_description = "Lead / Contact"

    def requirement_summary(self, obj):
        if obj.property:
            return format_html(
                '<a href="{}" target="_blank">{}</a><br><small>₹{}/mo</small>',
                obj.property.get_absolute_url(), obj.property.title[:35], f"{obj.property.rent:,}"
            )
        return format_html(
            '<span>{}</span><br><small class="text-muted">Budget: ₹{} - ₹{}</small>',
            obj.bhk or "General Rental", f"{obj.min_budget or 0:,}", f"{obj.max_budget or 0:,}"
        )
    requirement_summary.short_description = "Requirement / Property"

    def source_badge(self, obj):
        colors = {
            'Google': '#ea4335',
            'Facebook': '#1877f2',
            'Instagram': '#c32aa3',
            'WhatsApp': '#25d366',
            'Advertisement': '#f59e0b',
            'Direct': '#64748b',
            'Website': '#0d9488',
        }
        color = colors.get(obj.source, '#64748b')
        campaign = f" | {obj.utm_campaign}" if obj.utm_campaign else ""
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}{}'
            '</span>',
            color, obj.source, campaign
        )
    source_badge.short_description = "Source"

    def status_badge(self, obj):
        status_colors = {
            'new': '#ef4444',            # Red
            'contacted': '#f59e0b',      # Amber
            'interested': '#3b82f6',     # Blue
            'visit_scheduled': '#8b5cf6',# Purple
            'negotiation': '#ec4899',    # Pink
            'converted': '#10b981',      # Emerald Green
            'not_interested': '#94a3b8', # Slate
            'closed': '#64748b',         # Dark Gray
        }
        color = status_colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="border-left: 4px solid {}; padding-left: 6px; font-weight: 600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Pipeline Status"

    def quick_actions(self, obj):
        tel_link = f"tel:{obj.clean_phone}"
        wa_url = build_lead_followup_whatsapp_url(obj)
        email_link = f"mailto:{obj.email}" if obj.email else ""

        buttons = [
            f'<a href="{tel_link}" title="Call Lead" style="display:inline-block; margin-right:4px; padding:3px 7px; background:#e0f2fe; color:#0369a1; border-radius:4px; text-decoration:none; font-size:12px;">📞 Call</a>',
            f'<a href="{wa_url}" target="_blank" title="WhatsApp Lead" style="display:inline-block; margin-right:4px; padding:3px 7px; background:#dcfce7; color:#15803d; border-radius:4px; text-decoration:none; font-size:12px;">💬 WA</a>',
        ]
        if email_link:
            buttons.append(f'<a href="{email_link}" title="Email Lead" style="display:inline-block; padding:3px 7px; background:#f1f5f9; color:#475569; border-radius:4px; text-decoration:none; font-size:12px;">✉️ Mail</a>')
        return format_html(''.join(buttons))
    quick_actions.short_description = "Quick Reach"

    # Bulk status action methods
    actions = ['mark_as_contacted', 'mark_as_interested', 'mark_as_visit_scheduled', 'mark_as_converted']

    @admin.action(description="Mark selected leads as Contacted")
    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted')

    @admin.action(description="Mark selected leads as Interested")
    def mark_as_interested(self, request, queryset):
        queryset.update(status='interested')

    @admin.action(description="Mark selected leads as Visit Scheduled")
    def mark_as_visit_scheduled(self, request, queryset):
        queryset.update(status='visit_scheduled')

    @admin.action(description="Mark selected leads as Converted (Deal Closed)")
    def mark_as_converted(self, request, queryset):
        queryset.update(status='converted')
