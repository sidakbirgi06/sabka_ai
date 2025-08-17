# in seller/forms.py
from django import forms
from .models import BusinessProfile, ChatbotSettings

#FORMS OF BUSINESS INFO PAGE SECTION 1
class BusinessProfileStep1Form(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'owner_name', 'contact_number', 'business_email', 'address', 'operating_hours']

#FORMS OF BUSINESS INFO PAGE SECTION 2
class BusinessProfileStep2Form(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['usp', 'target_market', 'audience_profile']

#FORMS OF BUSINESS INFO PAGE SECTION 3
class BusinessProfileStep3Form(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['product_categories', 'inventory_update_frequency', 'top_selling_products', 'combo_packs']

#FORMS OF BUSINESS INFO PAGE SECTION 4
class BusinessProfileStep4Form(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['accepts_cod', 'accepts_upi', 'accepts_card', 'delivery_methods', 'return_policy']

#FORMS OF BUSINESS INFO PAGE SECTION 5
class BusinessProfileStep5Form(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['faqs']

#FORMS FOR CHATBOT SETUP PAGE 1
class ChatbotSettingsStep1Form(forms.ModelForm):
    class Meta:
        model = ChatbotSettings
        fields = ['ai_name', 'personality', 'greeting', 'product_description_tone', 'use_emojis', 'phrases_to_avoid', 'signature_line']

#FORMS FOR CHATBOT SETUP PAGE 2
class ChatbotSettingsStep2Form(forms.ModelForm):
    class Meta:
        model = ChatbotSettings
        fields = [
            'product_presentation', 'allow_negotiation', 'max_discount_percent',
            'allow_upselling', 'collect_name', 'collect_phone',
            'collect_email', 'collect_address'
        ]        

#FORMS FOR CHATBOT SETUP PAGE 3
class ChatbotSettingsStep3Form(forms.ModelForm):
    class Meta:
        model = ChatbotSettings
        fields = [
            'error_handling_strategy', 'custom_error_reply',
            'human_escalation_keywords', 'high_priority_alert'
        ]