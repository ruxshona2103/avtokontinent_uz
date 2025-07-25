from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'position', 'start_date', 'end_date')
    list_filter = ('is_active',)
    search_fields = ('title',)

