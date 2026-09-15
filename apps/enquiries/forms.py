from django import forms
from .models import Enquiry
from apps.properties.models import Property

class BaseEnquiryForm(forms.ModelForm):
    """
    Base form with honeypot anti-spam protection and mobile number validation.
    """
    website_url_hp = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none !important;',
            'tabindex': '-1',
            'autocomplete': 'off',
        })
    )

    def clean_website_url_hp(self):
        val = self.cleaned_data.get('website_url_hp')
        if val:
            raise forms.ValidationError("Spam detected.")
        return val

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Please enter a valid 10-digit mobile number.")
        return phone


class PropertyEnquiryForm(BaseEnquiryForm):
    """
    Enquiry form used on individual property detail pages and modals.
    """
    class Meta:
        model = Enquiry
        fields = [
            'property', 'name', 'phone', 'email', 'whatsapp_number',
            'preferred_contact_method', 'message', 'city', 'bhk', 'min_budget', 'max_budget'
        ]
        widgets = {
            'property': forms.HiddenInput(),
            'city': forms.HiddenInput(),
            'bhk': forms.HiddenInput(),
            'min_budget': forms.HiddenInput(),
            'max_budget': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name *', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-Digit Mobile Number *', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address (Optional)'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp Number (If different)'}),
            'preferred_contact_method': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'I would like to arrange a site visit or get more information on this property...'}),
        }


class FindPropertyForm(BaseEnquiryForm):
    """
    Comprehensive requirement intake form for /find-property/.
    High-conversion layout with clear section grouping.
    """
    LOOKING_FOR_CHOICES = [
        ('Rent', 'Looking to Rent'),
        ('Lease', 'Long-term Company Lease'),
        ('Flatmate', 'Shared Accommodation / Flatmate'),
    ]

    PROPERTY_TYPE_CHOICES = [
        ('', 'Select Property Type'),
        ('Flat / Apartment', 'Flat / Apartment'),
        ('Independent Floor', 'Independent Floor'),
        ('Gated Villa / House', 'Gated Villa / House'),
        ('Studio Apartment', 'Studio Apartment'),
        ('Penthouse', 'Penthouse'),
    ]

    BHK_CHOICES = [
        ('', 'Select BHK *'),
        ('1 BHK', '1 BHK'),
        ('2 BHK', '2 BHK'),
        ('3 BHK', '3 BHK'),
        ('4 BHK', '4 BHK'),
        ('Studio / 1 RK', 'Studio / 1 RK'),
        ('5+ BHK / Luxury Villa', '5+ BHK / Luxury Villa'),
    ]

    FURNISHING_CHOICES = [
        ('', 'Any Furnishing'),
        ('Fully Furnished', 'Fully Furnished'),
        ('Semi-Furnished', 'Semi-Furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]

    MOVE_IN_CHOICES = [
        ('Immediately', 'Immediately / Ready to Move'),
        ('Within 15 Days', 'Within 15 Days'),
        ('Within 30 Days', 'Within 30 Days'),
        ('Next Month or Later', 'Next Month or Later'),
    ]

    looking_for = forms.ChoiceField(
        choices=LOOKING_FOR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    property_type = forms.ChoiceField(
        choices=PROPERTY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    bhk = forms.ChoiceField(
        choices=BHK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        required=True
    )
    furnishing = forms.ChoiceField(
        choices=FURNISHING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    move_in_date = forms.ChoiceField(
        choices=MOVE_IN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Enquiry
        fields = [
            'name', 'phone', 'email', 'whatsapp_number', 'preferred_contact_method',
            'looking_for', 'property_type', 'bhk', 'city', 'preferred_area',
            'min_budget', 'max_budget', 'furnishing', 'move_in_date', 'message'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rahul Sharma *', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9876543210 *', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. rahul@example.com'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Same as mobile or WhatsApp number'}),
            'preferred_contact_method': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Noida, Gurugram, Bengaluru *', 'required': 'required'}),
            'preferred_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sector 62, Golf Course Extn, Whitefield'}),
            'min_budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Budget (₹) e.g. 20000'}),
            'max_budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Budget (₹) e.g. 35000'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Family or bachelors, parking preference, pet friendly, preferred societies...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_b = cleaned_data.get('min_budget')
        max_b = cleaned_data.get('max_budget')  
        if min_b and max_b and min_b > max_b:
            raise forms.ValidationError("Minimum budget cannot exceed maximum budget.")
        return cleaned_data
