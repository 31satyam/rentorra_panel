from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Advertisement, AdvertisementClick
from apps.properties.models import Property

class AdvertisementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.property = Property.objects.create(
            title="Ad Target Property",
            property_type="flat",
            bhk="2_bhk",
            rent=30000,
            city="Gurugram",
            area="DLF Phase 5",
            address="Tower C",
            area_sqft=1400,
            status="available",
            description="Luxury ad target"
        )
        # 1x1 GIF dummy image
        tiny_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        self.image = SimpleUploadedFile("ad_banner.gif", tiny_gif, content_type="image/gif")
        self.ad = Advertisement.objects.create(
            title="Summer Special Offer",
            image=self.image,
            property=self.property,
            placement="homepage_banner",
            start_date=date.today() - timedelta(days=1),
            is_active=True
        )

    def test_active_ad_retrieval(self):
        """Test get_active_ad class method."""
        ad = Advertisement.get_active_ad("homepage_banner")
        self.assertIsNotNone(ad)
        self.assertEqual(ad.title, "Summer Special Offer")

    def test_ad_click_redirect_and_tracking(self):
        """Test clicking ad logs click in database and redirects."""
        initial_clicks = self.ad.total_clicks
        url = reverse('ad_click', kwargs={'ad_id': self.ad.id})
        response = self.client.get(url)

        # Should redirect to target property
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.property.get_absolute_url(), response.url)
        self.assertIn("utm_source=Rentorra", response.url)

        # Check click recorded in db
        self.assertEqual(self.ad.clicks.count(), initial_clicks + 1)
