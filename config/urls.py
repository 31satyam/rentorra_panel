from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.properties.models import Property, Location
from apps.enquiries.views import find_property_view

# SEO Sitemaps
class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Property.objects.filter(status='available')

    def lastmod(self, obj):
        return obj.updated_at


class LocationSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Location.objects.filter(is_active=True)


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return ['home', 'property_list', 'find_property', 'about', 'contact', 'privacy', 'terms']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'properties': PropertySitemap,
    'locations': LocationSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Lead-gen Requirement Intake (direct top-level URL as specified)
    path('find-property/', find_property_view, name='find_property'),
    
    # Internal Staff Lead Dashboard
    path('', include('apps.accounts.urls')),
    
    # Properties Catalog & Details
    path('properties/', include('apps.properties.urls')),
    
    # Enquiry Form Submissions
    path('enquiries/', include('apps.enquiries.urls')),
    
    # Advertisements & Click Tracking
    path('ads/', include('apps.advertisements.urls')),
    
    # Core Marketing & Info Pages
    path('', include('apps.core.urls')),
    
    # Dynamic SEO Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Static & Media serving during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Handlers
handler404 = 'apps.core.views.custom_404_view'
handler500 = 'apps.core.views.custom_500_view'

# Customize Django Admin Branding
admin.site.site_header = "Rentorra Property Lead Management"
admin.site.site_title = "Rentorra Admin"
admin.site.index_title = "Rentorra Real Estate Portal & Lead CRM"
