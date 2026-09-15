from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactMessage

class CorePagesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rentorra")
        self.assertContains(response, "Find Your Perfect Rental Home")

    def test_about_page_status(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Us")

    def test_contact_submission(self):
        post_data = {
            'name': 'Priya Nair',
            'phone': '9876543210',
            'email': 'priya@example.com',
            'subject': 'General Query',
            'message': 'Looking for corporate housing in Bengaluru.',
            'website_url_hp': '',
        }
        response = self.client.post(reverse('contact'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(name='Priya Nair').exists())

    def test_robots_and_sitemap(self):
        # robots.txt
        response_robots = self.client.get('/robots.txt')
        self.assertEqual(response_robots.status_code, 200)
        self.assertIn("User-agent: *", response_robots.content.decode())

        # sitemap.xml
        response_sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(response_sitemap.status_code, 200)
        self.assertEqual(response_sitemap['content-type'], 'application/xml')
