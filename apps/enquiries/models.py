import builtins
from django.db import models
from django.contrib.auth.models import User
from apps.properties.models import Property

class Enquiry(models.Model):
    """
    Central Lead Generation and Requirement Intake Model.
    Captures property inquiries, general tenant requirements, and full UTM attribution.
    """
    STATUS_CHOICES = [
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('visit_scheduled', 'Visit Scheduled'),
        ('negotiation', 'Negotiation'),
        ('converted', 'Converted (Deal Closed)'),
        ('not_interested', 'Not Interested'),
        ('closed', 'Closed / Lost'),
    ]

    SOURCE_CHOICES = [
        ('Website', 'Direct Website'),
        ('Google', 'Google Search / Ads'),
        ('Facebook', 'Facebook Ads'),
        ('Instagram', 'Instagram Ads'),
        ('WhatsApp', 'WhatsApp Referral'),
        ('Advertisement', 'Portal Advertisement'),
        ('Direct', 'Direct / Unknown'),
        ('Other', 'Other'),
    ]

    PREFERRED_CONTACT_CHOICES = [
        ('call', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]

    # Associated Property (optional, populated when enquiry is submitted on property detail)
    property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='enquiries', help_text="Specific property being enquired about"
    )

    # Lead Contact Information
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    preferred_contact_method = models.CharField(
        max_length=20, choices=PREFERRED_CONTACT_CHOICES, default='call'
    )

    # Requirement Specifications
    looking_for = models.CharField(max_length=100, default='Rent', blank=True)
    property_type = models.CharField(max_length=50, blank=True)
    bhk = models.CharField(max_length=30, blank=True, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    preferred_area = models.CharField(max_length=150, blank=True)
    min_budget = models.PositiveIntegerField(null=True, blank=True)
    max_budget = models.PositiveIntegerField(null=True, blank=True)
    furnishing = models.CharField(max_length=50, blank=True)
    move_in_date = models.CharField(max_length=100, blank=True, help_text="e.g. Immediately, Within 15 Days, Next Month")
    message = models.TextField(blank=True, help_text="Specific requirements, pet preferences, parking need, etc.")

    # Attribution & Tracking
    source = models.CharField(max_length=50, default='Website', db_index=True)
    utm_source = models.CharField(max_length=150, blank=True)
    utm_medium = models.CharField(max_length=150, blank=True)
    utm_campaign = models.CharField(max_length=200, blank=True)
    utm_term = models.CharField(max_length=200, blank=True)
    utm_content = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    # Sales Pipeline & CRM Fields
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new', db_index=True)
    admin_remark = models.TextField(blank=True, help_text="Internal notes by sales/leasing team")
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_enquiries', help_text="Sales representative handling this lead"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Enquiry & Lead'
        verbose_name_plural = 'Enquiries & Leads'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['city', 'bhk']),
        ]

    def __str__(self):
        target = self.property.title if self.property else f"{self.bhk} in {self.city}"
        return f"{self.name} ({self.phone}) - {target} [{self.get_status_display()}]"

    @builtins.property
    def clean_phone(self):
        """Standardized digits for tel: links"""
        return ''.join(c for c in self.phone if c.isdigit() or c == '+')

    @builtins.property
    def clean_whatsapp(self):
        """Standardized digits for wa.me links"""
        digits = ''.join(c for c in (self.whatsapp_number or self.phone) if c.isdigit())
        if digits.startswith('0'):
            digits = '91' + digits[1:]
        elif len(digits) == 10:
            digits = '91' + digits
        return digits
