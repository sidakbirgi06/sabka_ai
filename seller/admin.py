from django.contrib import admin
from .models import BusinessProfile, ChatbotSettings # Import our models

# Register your models here.
# This tells Django to show these models in the admin site.
admin.site.register(BusinessProfile)
admin.site.register(ChatbotSettings)
