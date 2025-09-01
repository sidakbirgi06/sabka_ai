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
    print(f"[DEBUG] update_business_profile called with updates: {updates}")

    if not updates:
        return "No update information was provided."

    try:
        profile = BusinessProfile.objects.get(user=user)
        print(f"[DEBUG] Found profile for user: {user.username}")
        
        updated_fields = []
        for field, value in updates.items():
            if hasattr(profile, field):
                print(f"[DEBUG] About to update field '{field}' to '{value}'")
                setattr(profile, field, value)
                updated_fields.append(field)
            else:
                print(f"[DEBUG] Error: Field '{field}' does not exist.")
                return f"Error: The field '{field}' does not exist in the Business Profile."

        if not updated_fields:
            return "None of the provided fields matched the Business Profile."

        # MODIFIED THIS LINE TO BE MORE EXPLICIT
        profile.save(update_fields=updated_fields)
        print(f"[DEBUG] profile.save() called for fields: {updated_fields}")
        
        return f"Successfully updated the following fields: {', '.join(updated_fields)}."

    except BusinessProfile.DoesNotExist:
        print(f"[DEBUG] Error: Business profile not found for user: {user.username}")
        return "The user has not created a business profile yet. Cannot update."
    except Exception as e:
        print(f"[DEBUG] An unexpected error occurred: {e}")
        return f"An unexpected error occurred while trying to update: {e}"