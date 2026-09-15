import builtins
from django.db import models
from django.utils import timezone
from apps.properties.models import Property

class Advertisement(models.Model):
    """
    Marketing and promotional banner advertisements placed across Rentorra.
    """
    PLACEMENT_CHOICES = [
        ('homepage_hero', 'Homepage Hero'),
        ('homepage_banner', 'Homepage Banner'),
        ('property_listing', 'Property Listing Top/Inline'),
        ('property_detail', 'Property Detail Sidebar'),
        ('sidebar', 'General Sidebar'),
        ('popup', 'Lead Modal / Popup'),
    ]

    title = models.CharField(max_length=200, help_text="Campaign name or promotional headline")
    image = models.ImageField(upload_to='advertisements/%Y/%m/', help_text="Promotional banner asset")
    description = models.TextField(blank=True, help_text="Subtext or promotional callout")
    property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='promotions', help_text="Optional: direct link to a featured property listing"
    )
    target_url = models.URLField(
        blank=True,
        help_text="Destination URL (if not directly linked to a property). Can include UTM parameters."
    )
    placement = models.CharField(max_length=40, choices=PLACEMENT_CHOICES, default='homepage_banner', db_index=True)
    start_date = models.DateField(default=timezone.now, help_text="Campaign start date")
    end_date = models.DateField(null=True, blank=True, help_text="Campaign expiration date (optional)")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-created_at']
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'

    def __str__(self):
        return f"{self.title} ({self.get_placement_display()})"

    @classmethod
    def get_active_ad(cls, placement):
        """
        Retrieves the most recent active advertisement for a given placement.
        """
        today = timezone.now().date()
        qs = cls.objects.filter(
            placement=placement,
            is_active=True,
            start_date__lte=today
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
        )
        return qs.first()

    @builtins.property
    def destination_url(self):
        """Returns the target URL or the linked property's URL."""
        if self.property:
            return self.property.get_absolute_url()
        return self.target_url or '#'

    @builtins.property
    def total_clicks(self):
        return self.clicks.count()


class AdvertisementClick(models.Model):
    """
    Analytics record tracking each user click on an advertisement banner.
    """
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    referrer = models.URLField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Advertisement Click'
        verbose_name_plural = 'Advertisement Clicks'

    def __str__(self):
        return f"Click on {self.advertisement.title} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
