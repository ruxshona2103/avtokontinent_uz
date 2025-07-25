from rest_framework import serializers
from setting.models import SiteSettings

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['dollar_rate', 'card_number']
