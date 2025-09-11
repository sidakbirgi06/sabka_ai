from .models import BusinessProfile
import json
from django.contrib.auth.models import User
from .models import BusinessProfile


# BUSINESS PROFILE -> GETTER
def get_entire_business_profile(user) -> str:
    """
    Retrieves the COMPLETE business profile for the logged-in user.
    This includes all 5 sections: Core Identity, Brand, Products, Operations, and FAQs.
    """
    try:
        profile = BusinessProfile.objects.get(user=user)
        
        all_data = {
            # --- Section 1: Core Business Identity ---
            "business_name": profile.business_name,
            "owner_name": profile.owner_name,
            "contact_number": profile.contact_number,
            "business_email": profile.business_email,
            "address": profile.address,
            "operating_hours": profile.operating_hours,
            "social_media_links": profile.social_media_links,

            # --- Section 2: Your Brand & Customers ---
            "usp": profile.usp,
            "target_market": profile.target_market,
            "audience_profile": profile.audience_profile,

            # --- Section 3: Products & Inventory ---
            "product_categories": profile.product_categories,
            "inventory_update_frequency": profile.inventory_update_frequency,
            "top_selling_products": profile.top_selling_products,
            "combo_packs": profile.combo_packs,
            
            # --- Section 4: How You Operate ---
            "accepts_cod": profile.accepts_cod,
            "accepts_upi": profile.accepts_upi,
            "accepts_card": profile.accepts_card,
            "delivery_methods": profile.delivery_methods,
            "return_policy": profile.return_policy,

            # --- Section 5: FAQs ---
            "faqs": profile.faqs,
        }
        return json.dumps(all_data, indent=2)

    except BusinessProfile.DoesNotExist:
        return "The user has not created a business profile yet."


# BUSINESS PROFILE ->  SETTER
def update_business_profile(user: User, **updates: dict) -> dict:
    """
    Updates one or more fields in the user's BusinessProfile.
    """
    # ... (the beginning of your function is the same)
    try:
        profile = BusinessProfile.objects.get(user=user)
    except BusinessProfile.DoesNotExist:
        return {"status": "error", "message": "Business profile not found."}

    fields_to_update = []
    for field, value in updates.items():
        if hasattr(profile, field):
            setattr(profile, field, value)
            fields_to_update.append(field)
        else:
            # This is a good check to have for debugging
            print(f"[DEBUG] Field '{field}' does not exist on BusinessProfile model.")

    if not fields_to_update:
        return {"status": "error", "message": "No valid fields were provided for update."}

    try:
        # Use the debugging print statements we created before
        print(f"[DEBUG] About to update fields {fields_to_update} with values {updates}")
        profile.save(update_fields=fields_to_update)
        print(f"[DEBUG] profile.save() called for fields: {fields_to_update}")
        
        # --- KEY CHANGE ---
        # Instead of a string, return a structured dictionary
        return {
            "status": "success",
            "message": f"Successfully updated the following fields: {', '.join(fields_to_update)}",
            "updated_fields": fields_to_update
        }
    except Exception as e:
        print(f"[ERROR] Failed to save profile for user {user.id}: {e}")
        return {"status": "error", "message": f"An error occurred while saving: {e}"}


# ADD THE IMPORTS IN UTILS PY AFTER ADDING INFO ABOUT CHATBOT SET UP OR ANY PAGE TOO