from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Property, Location, Amenity, PropertyImage

class PropertyModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.location = Location.objects.create(
            city="Noida",
            area="Sector 62",
            description="Prime IT Hub"
        )
        self.amenity = Amenity.objects.create(
            name="Lift",
            icon_class="bi-arrow-down-up"
        )
        self.property = Property.objects.create(
            title="Spacious 2 BHK in Sector 62",
            property_type="flat",
            bhk="2_bhk",
            rent=25000,
            security_deposit=50000,
            location=self.location,
            address="Tower A, Green Heights",
            area_sqft=1100,
            status="available",
            is_featured=True,
            description="Sunny flat with modular kitchen."
        )
        self.property.amenities.add(self.amenity)

    def test_property_slug_generation(self):
        """Test automatic SEO slug generation."""
        self.assertTrue(self.property.slug)
        self.assertIn("2-bhk", self.property.slug)
        self.assertIn("sector-62", self.property.slug)

    def test_property_listing_view(self):
        """Test listing catalog view and filters."""
        url = reverse('property_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spacious 2 BHK in Sector 62")
        self.assertContains(response, "₹25,000")

    def test_property_filter_by_city(self):
        """Test filtering by city."""
        url = reverse('property_list') + "?city=Noida"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spacious 2 BHK in Sector 62")

        url_empty = reverse('property_list') + "?city=Mumbai"
        response_empty = self.client.get(url_empty)
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, "Spacious 2 BHK in Sector 62")

    def test_property_detail_view(self):
        """Test property detail view response and contents."""
        url = self.property.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)
        self.assertContains(response, "₹25,000")
        self.assertContains(response, "Lift")
        # Check WhatsApp link presence
        self.assertContains(response, "wa.me")
