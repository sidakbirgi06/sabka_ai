from django.contrib import admin
from .models import BusinessProfile, ChatbotSettings, SocialConnection, Conversation, Message, AssistantConversation, AssistantChatMessage

# Register your models here.
# This tells Django to show these models in the admin site.
admin.site.register(BusinessProfile)
admin.site.register(ChatbotSettings)
admin.site.register(SocialConnection)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(AssistantConversation)
admin.site.register(AssistantChatMessage)
