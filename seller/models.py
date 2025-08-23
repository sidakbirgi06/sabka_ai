from django.db import models
from django.contrib.auth.models import User


# FIELDS FOR BUSINESS FORM PAGE
class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # SECTION 1 OF BUSINESS INFO PAGE
    business_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner_name = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    business_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    operating_hours = models.CharField(max_length=100, blank=True)
    social_media_links = models.TextField(
        blank=True, 
        null=True, 
        help_text="Optional. Enter your social media links, one per line."
    )

    # SECTION 2 OF BUSINESS INFO PAGE
    usp = models.TextField(verbose_name="Unique Selling Proposition (USP)", blank=True, help_text="What makes your business special?")
    target_market = models.CharField(max_length=255, blank=True, help_text="e.g., college students, young professionals")
    audience_profile = models.TextField(verbose_name="Ideal Customer Profile", blank=True)

    #SECTION 3 OF BUSINESS INFO PAGE
    UPDATE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('OCCASIONALLY', 'Occasionally'),
    ]
    product_categories = models.TextField(verbose_name="Main Product Categories", blank=True, help_text="Separate with commas, e.g., T-shirts, Jeans, Shoes")
    inventory_update_frequency = models.CharField(verbose_name="Inventory Update Frequency", max_length=20, choices=UPDATE_CHOICES, blank=True)
    top_selling_products = models.TextField(verbose_name="Top-Selling Products or New Arrivals", blank=True, help_text="List a few examples for the AI to use.")
    combo_packs = models.TextField(verbose_name="Special Combos or Packs", blank=True, help_text="Describe any special deals, e.g., 'Buy 2 T-shirts, get 1 free'")

    #SECTION 4 OF BUSINESS INFO PAGE
    accepts_cod = models.BooleanField(verbose_name="Accept Cash on Delivery (COD)", default=False)
    accepts_upi = models.BooleanField(verbose_name="Accept UPI (PayTM, GPay, etc.)", default=False)
    accepts_card = models.BooleanField(verbose_name="Accept Credit/Debit Card", default=False)
    delivery_methods = models.TextField(verbose_name="Delivery Methods You Offer", blank=True, help_text="e.g., Local hand-delivery, Courier service, In-store pickup")
    return_policy = models.TextField(verbose_name="Your Return/Refund Policy", blank=True)

    #SECTION 5 OF BUSINESS INFO PAGE
    faqs = models.TextField(verbose_name="Frequently Asked Questions (FAQs)", blank=True, help_text="List common questions and their answers. e.g., Q: Do you offer discounts? A: Yes, on orders above 2000.")




    def __str__(self):
        return self.business_name
    
    class Meta:
        verbose_name_plural = "Business profiles"
    
    
    
    
# FIELDS FOR CHATBOT SETTING PAGE
class ChatbotSettings(models.Model):
    # This links settings to a specific business profile, not just a user.
    business_profile = models.OneToOneField(BusinessProfile, on_delete=models.CASCADE)

# SECTION 1 OF CHATBOT SETUP PAGE
    ai_name = models.CharField(max_length=100, blank=True, verbose_name="AI Assistant's Name", help_text="Leave blank to use your business name.")
    personality = models.TextField(verbose_name="AI Personality", blank=True, help_text="e.g., Friendly and casual, Formal and professional, Witty and humorous")
    greeting = models.CharField(max_length=255, blank=True, verbose_name="Customer Greeting Message")
    product_description_tone = models.TextField(verbose_name="Tone for Product Descriptions", blank=True)
    use_emojis = models.BooleanField(verbose_name="Use Emojis in Conversation?", default=True)
    phrases_to_avoid = models.TextField(verbose_name="Phrases AI Should Avoid", blank=True, help_text="Separate phrases with a comma.")
    signature_line = models.CharField(max_length=150, verbose_name="Signature Closing Line", blank=True, help_text="e.g., Happy to help!")

#SECTION 2 OF CHATBOT SETUP PAGE
    PRESENTATION_CHOICES = [
        ('TEXT_ONLY', 'Text description only'),
        ('IMAGE_FIRST', 'Image first, then text'),
        ('TEXT_WITH_PRICE', 'Text with price, then image'),
    ]
    product_presentation = models.CharField(max_length=20, choices=PRESENTATION_CHOICES, default='TEXT_ONLY', verbose_name="How should the AI present products?")

    allow_negotiation = models.BooleanField(verbose_name="Allow AI to Negotiate on Price?", default=False)
    max_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Maximum Discount Percentage (%)", help_text="e.g., enter 10.00 for 10%")
    allow_upselling = models.BooleanField(verbose_name="Allow AI to Upsell (suggest related products)?", default=False)

    # Fields for customer details to collect
    collect_name = models.BooleanField(verbose_name="Full Name", default=True)
    collect_phone = models.BooleanField(verbose_name="Phone Number", default=True)
    collect_email = models.BooleanField(verbose_name="Email Address", default=False)
    collect_address = models.BooleanField(verbose_name="Delivery Address", default=True)

#SECTION 3 OF CHATBOT SETUP PAGE
    ERROR_HANDLING_CHOICES = [
        ('REPHRASE', 'Ask the customer to rephrase the question'),
        ('HANDOVER', 'Immediately say a human will take over'),
    ]
    error_handling_strategy = models.CharField(max_length=20, choices=ERROR_HANDLING_CHOICES, default='HANDOVER', verbose_name="If the AI doesn't understand, what should it do?")
    custom_error_reply = models.CharField(max_length=255, blank=True, verbose_name="Custom reply when confused", help_text="e.g., I'm not sure, but a team member will get back to you shortly.")
    human_escalation_keywords = models.TextField(verbose_name="Keywords for Human Escalation", blank=True, help_text="List words that should immediately notify you (separate with commas). e.g., complaint, angry, legal")
    high_priority_alert = models.BooleanField(verbose_name="High-priority alert if a customer asks to call?", default=True)





    def __str__(self):
        # A helpful name for this object
        return f"Settings for {self.business_profile.business_name}"
    
    class Meta:
        verbose_name_plural = "Chatbot settings"



class FacebookPage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    page_id = models.CharField(max_length=100, unique=True)
    page_name = models.CharField(max_length=255)
    page_access_token = models.TextField()

    def __str__(self):
        return f"{self.page_name} for {self.user.username}"