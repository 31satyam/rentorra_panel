import builtins
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator

class Location(models.Model):
    """
    Geographic location representing cities and micro-markets (areas/sectors).
    Used for filtering and dynamic SEO landing pages.
    """
    city = models.CharField(max_length=100, db_index=True)
    area = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Editorial overview of the neighbourhood.")
    is_active = models.BooleanField(default=True, db_index=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        ordering = ['city', 'area']
        unique_together = ('city', 'area')
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f"{self.area}, {self.city}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.area}-{self.city}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('properties_by_location', kwargs={'slug': self.slug})


class Amenity(models.Model):
    """
    Reusable residential amenities (Lift, Security, Gym, Power Backup, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(
        max_length=50,
        default='bi-check-circle',
        help_text="Bootstrap Icon class, e.g., 'bi-car-front', 'bi-lightning-charge', 'bi-shield-check'"
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class Property(models.Model):
    """
    Primary rental property listing model.
    """
    PROPERTY_TYPE_CHOICES = [
        ('flat', 'Flat / Apartment'),
        ('independent_floor', 'Independent Floor'),
        ('villa', 'Villa / House'),
        ('studio', 'Studio Apartment'),
        ('penthouse', 'Penthouse'),
    ]

    BHK_CHOICES = [
        ('1_rk', '1 RK'),
        ('1_bhk', '1 BHK'),
        ('2_bhk', '2 BHK'),
        ('3_bhk', '3 BHK'),
        ('4_bhk', '4 BHK'),
        ('5_bhk_plus', '5+ BHK'),
    ]

    FURNISHING_CHOICES = [
        ('unfurnished', 'Unfurnished'),
        ('semi_furnished', 'Semi-Furnished'),
        ('fully_furnished', 'Fully Furnished'),
    ]

    PARKING_CHOICES = [
        ('none', 'None'),
        ('two_wheeler', 'Two-Wheeler Only'),
        ('1_car', '1 Covered Car Parking'),
        ('2_cars', '2 Covered Car Parkings'),
        ('open_parking', 'Open Parking'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('inactive', 'Inactive'),
    ]

    # Core Identifiers
    title = models.CharField(max_length=250, help_text="Descriptive title e.g. 'Spacious 2 BHK Flat in Sector 62'")
    slug = models.SlugField(max_length=300, unique=True, blank=True, db_index=True)
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPE_CHOICES, default='flat', db_index=True)
    bhk = models.CharField(max_length=20, choices=BHK_CHOICES, default='2_bhk', db_index=True)
    description = models.TextField(help_text="Detailed property description, layout specs, and tenant preferences.")

    # Financials
    rent = models.PositiveIntegerField(help_text="Monthly rent in Indian Rupees (INR)", db_index=True)
    security_deposit = models.PositiveIntegerField(default=0, help_text="Security deposit in INR")
    maintenance_charges = models.PositiveIntegerField(default=0, help_text="Monthly maintenance charges in INR (if any)")

    # Geographic Location
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='properties', help_text="Linked city and area"
    )
    city = models.CharField(max_length=100, db_index=True)
    area = models.CharField(max_length=150, db_index=True)
    address = models.CharField(max_length=300)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Physical Specifications
    area_sqft = models.PositiveIntegerField(help_text="Super built-up or carpet area in sq. ft.")
    bedrooms = models.PositiveSmallIntegerField(default=2)
    bathrooms = models.PositiveSmallIntegerField(default=2)
    balconies = models.PositiveSmallIntegerField(default=1)
    furnishing = models.CharField(max_length=30, choices=FURNISHING_CHOICES, default='semi_furnished', db_index=True)
    parking = models.CharField(max_length=30, choices=PARKING_CHOICES, default='1_car')
    floor_no = models.CharField(max_length=20, default='4th of 14', blank=True)
    facing = models.CharField(max_length=30, default='North-East', blank=True)
    age_of_property = models.CharField(max_length=50, default='0-3 Years', blank=True)

    # Availability & Administrative Status
    available_from = models.DateField(null=True, blank=True, help_text="Date from which property is ready for move-in")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True, help_text="Show in featured carousel/cards")

    # Relationships
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='properties')

    # SEO Metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        indexes = [
            models.Index(fields=['city', 'bhk', 'status']),
            models.Index(fields=['rent', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - ₹{self.rent:,}/mo ({self.get_bhk_display()})"

    def save(self, *args, **kwargs):
        # Auto-sync city and area from linked Location if selected
        if self.location:
            if not self.city:
                self.city = self.location.city
            if not self.area:
                self.area = self.location.area

        if not self.slug:
            base_slug = slugify(f"{self.get_bhk_display()}-{self.get_property_type_display()}-{self.area}-{self.city}")
            unique_slug = base_slug
            num = 1
            while Property.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        # Auto-populate meta tags if blank
        if not self.meta_title:
            self.meta_title = f"{self.get_bhk_display()} for Rent in {self.area}, {self.city} | Rentorra"
        if not self.meta_description:
            self.meta_description = f"Rent this {self.get_bhk_display()} ({self.area_sqft} sq.ft) in {self.area}, {self.city} for ₹{self.rent:,}/month. {self.get_furnishing_display()} with verified amenities."

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'slug': self.slug})

    @builtins.property
    def primary_image(self):
        """Returns the primary image, or first available image, or None."""
        first = self.images.filter(is_primary=True).first()
        if not first:
            first = self.images.first()
        return first

    @builtins.property
    def formatted_rent(self):
        """Format rent cleanly (e.g. ₹28,000)."""
        return f"₹{self.rent:,}"

    @builtins.property
    def formatted_deposit(self):
        return f"₹{self.security_deposit:,}" if self.security_deposit else "Negotiable"


class PropertyImage(models.Model):
    """
    Multiple photography assets attached to a property listing.
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/%Y/%m/')
    alt_text = models.CharField(max_length=200, blank=True, help_text="Descriptive text for accessibility & SEO")
    display_order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-is_primary', 'id']
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'

    def __str__(self):
        return f"Image for {self.property.title} (Order: {self.display_order})"

    def save(self, *args, **kwargs):
        # Auto-fill alt text if blank
        if not self.alt_text and self.property:
            self.alt_text = f"{self.property.title} - View {self.display_order + 1}"
        # If this image is marked primary, unmark any existing primary images for this property
        if self.is_primary and self.property_id:
            PropertyImage.objects.filter(property_id=self.property_id, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
