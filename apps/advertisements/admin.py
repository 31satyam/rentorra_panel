from django.contrib import admin
from django.utils.html import format_html
from .models import Advertisement, AdvertisementClick

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'placement', 'status_preview', 'total_clicks_count', 'start_date', 'end_date', 'is_active')
    list_filter = ('placement', 'is_active', 'start_date')
    search_fields = ('title', 'description', 'target_url')
    list_editable = ('is_active',)

    def status_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 35px; border-radius: 4px; object-fit: contain;" />', obj.image.url)
        return "No image"
    status_preview.short_description = "Banner Preview"

    def total_clicks_count(self, obj):
        return obj.total_clicks
    total_clicks_count.short_description = "Clicks"


@admin.register(AdvertisementClick)
class AdvertisementClickAdmin(admin.ModelAdmin):
    list_display = ('advertisement', 'ip_address', 'timestamp', 'referrer')
    list_filter = ('advertisement', 'timestamp')
    readonly_fields = ('advertisement', 'ip_address', 'user_agent', 'referrer', 'timestamp')
    ordering = ('-timestamp',)
