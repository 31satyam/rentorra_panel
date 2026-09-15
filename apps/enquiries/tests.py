from django.test import TestCase, Client
from django.urls import reverse
from .models import Enquiry
from apps.properties.models import Property

class EnquirySubmissionAndUTMTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.property = Property.objects.create(
            title="Sample 1 BHK in Noida",
            property_type="flat",
            bhk="1_bhk",
            rent=18000,
            city="Noida",
            area="Sector 75",
            address="CapeTown Sector 75",
            area_sqft=650,
            status="available",
            description="Cozy studio"
        )

    def test_find_property_submission_with_utm(self):
        """Test visiting page with UTM params, navigating, and submitting enquiry."""
        # 1. Visit with UTM params
        utm_url = reverse('find_property') + "?utm_source=facebook&utm_medium=cpc&utm_campaign=noida_leads"
        self.client.get(utm_url)

        # 2. Check UTM stored in session
        session = self.client.session
        self.assertIn('utm_params', session)
        self.assertEqual(session['utm_params']['utm_source'], 'facebook')
        self.assertEqual(session['utm_params']['utm_campaign'], 'noida_leads')

        # 3. Submit Find Property form
        post_data = {
            'name': 'Rahul Verma',
            'phone': '9876543210',
            'email': 'rahul@example.com',
            'city': 'Noida',
            'bhk': '2 BHK',
            'looking_for': 'Rent',
            'min_budget': 20000,
            'max_budget': 30000,
            'website_url_hp': '',  # Honeypot empty (valid human)
        }
        submit_url = reverse('find_property')
        response = self.client.post(submit_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # 4. Verify saved in database with UTM tags
        enquiry = Enquiry.objects.filter(phone='9876543210').first()
        self.assertIsNotNone(enquiry)
        self.assertEqual(enquiry.name, 'Rahul Verma')
        self.assertEqual(enquiry.utm_source, 'facebook')
        self.assertEqual(enquiry.utm_campaign, 'noida_leads')
        self.assertEqual(enquiry.status, 'new')

    def test_honeypot_spam_rejection(self):
        """Bots filling out the honeypot field should be rejected."""
        post_data = {
            'name': 'Spam Bot',
            'phone': '9876543210',
            'city': 'Noida',
            'bhk': '2 BHK',
            'looking_for': 'Rent',
            'website_url_hp': 'http://spam-link.com',  # Honeypot filled by bot
        }
        response = self.client.post(reverse('find_property'), post_data)
        # Form has errors, not redirected to success
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Enquiry.objects.filter(name='Spam Bot').exists())

    def test_required_field_validation(self):
        """Missing required phone or city should raise form validation errors."""
        post_data = {
            'name': 'Test User',
            'phone': '',  # Missing phone
            'city': '',   # Missing city
            'bhk': '',
        }
        response = self.client.post(reverse('find_property'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'phone', 'This field is required.')
        self.assertFormError(response.context['form'], 'city', 'This field is required.')
