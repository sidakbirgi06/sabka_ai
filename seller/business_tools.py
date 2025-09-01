from .models import BusinessProfile
import json

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
def update_business_profile(user, **updates) -> str:
    """
    Updates one or more fields in the user's business profile.
    Provide field names as arguments with their new values.
    Example: update_business_profile(user, business_name="New Name", operating_hours="9-5")
    """
    if not updates:
        return "No update information was provided."

    try:
        profile = BusinessProfile.objects.get(user=user)
        
        updated_fields = []
        for field, value in updates.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
                updated_fields.append(field)
            else:
                return f"Error: The field '{field}' does not exist in the Business Profile."

        if not updated_fields:
            return "None of the provided fields matched the Business Profile."

        profile.save()
        
        return f"Successfully updated the following fields: {', '.join(updated_fields)}."

    except BusinessProfile.DoesNotExist:
        return "The user has not created a business profile yet. Cannot update."