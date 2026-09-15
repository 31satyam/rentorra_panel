from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage, Amenity, Location

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3
    fields = ('image', 'alt_text', 'display_order', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, instance):
        if instance.image:
            return format_html('<img src="{}" style="max-height: 60px; border-radius: 4px;" />', instance.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview',
        'title',
        'bhk',
        'property_type',
        'rent_display',
        'area',
        'city',
        'status',
        'is_featured',
        'created_at'
    )
    list_display_links = ('thumbnail_preview', 'title')
    list_filter = ('status', 'is_featured', 'bhk', 'property_type', 'city', 'furnishing', 'created_at')
    search_fields = ('title', 'description', 'city', 'area', 'address', 'pincode', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('amenities',)
    inlines = [PropertyImageInline]
    list_editable = ('status', 'is_featured')
    list_per_page = 20
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'property_type', 'bhk', 'description', 'status', 'is_featured')
        }),
        ('Pricing & Financials', {
            'fields': ('rent', 'security_deposit', 'maintenance_charges')
        }),
        ('Location Details', {
            'fields': ('location', 'city', 'area', 'address', 'pincode', 'latitude', 'longitude')
        }),
        ('Specs & Features', {
            'fields': ('area_sqft', 'bedrooms', 'bathrooms', 'balconies', 'furnishing', 'parking', 'floor_no', 'facing', 'age_of_property', 'available_from')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('SEO Metadata', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description')
        }),
    )

    def thumbnail_preview(self, obj):
        img = obj.primary_image
        if img and img.image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />', img.image.url)
        return "No Photo"
    thumbnail_preview.short_description = "Photo"

    def rent_display(self, obj):
        return f"₹{obj.rent:,}"
    rent_display.short_description = "Rent / Mo"
    rent_display.admin_order_field = 'rent'

    actions = ['mark_as_available', 'mark_as_rented', 'toggle_featured']

    @admin.action(description="Mark selected properties as Available")
    def mark_as_available(self, request, queryset):
        queryset.update(status='available')

    @admin.action(description="Mark selected properties as Rented")
    def mark_as_rented(self, request, queryset):
        queryset.update(status='rented')

    @admin.action(description="Toggle Featured badge on selected properties")
    def toggle_featured(self, request, queryset):
        for prop in queryset:
            prop.is_featured = not prop.is_featured
            prop.save(update_fields=['is_featured'])


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class', 'is_featured', 'property_count')
    list_editable = ('icon_class', 'is_featured')
    search_fields = ('name',)

    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = "Properties"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('area', 'city', 'slug', 'is_active', 'properties_count')
    list_filter = ('city', 'is_active')
    search_fields = ('area', 'city', 'slug')
    prepopulated_fields = {'slug': ('area', 'city')}
    list_editable = ('is_active',)

    def properties_count(self, obj):
        return obj.properties.count()
    properties_count.short_description = "Active Listings"
