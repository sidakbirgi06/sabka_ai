import json
from django.contrib.auth.models import User
from .models import BusinessProfile

# BUSINESS PROFILE -> GETTER
def get_entire_business_profile(user_id: int) -> str:
    """
    Retrieves the COMPLETE business profile for a given user ID.
    The AI model will use this to get information about the user's business.
    """
    try:
        # --- CHANGE 1: We now look up the user by their ID ---
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)
        
        all_data = {
            # --- (This entire dictionary of your fields remains exactly the same) ---
            "business_name": profile.business_name,
            "owner_name": profile.owner_name,
            # ... and so on for all your fields
            "faqs": profile.faqs,
        }
        return json.dumps(all_data, indent=2)

    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return json.dumps({"error": "Profile not found for this user."})


# BUSINESS PROFILE -> SETTER
def update_business_profile(user_id: int, **updates: dict) -> dict:
    """
    Updates one or more fields in the BusinessProfile for a given user ID.
    """
    try:
        # --- CHANGE 2: We also look up the user by their ID here ---
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)
    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return {"status": "error", "message": "Business profile not found."}

    fields_to_update = []
    for field, value in updates.items():
        if hasattr(profile, field):
            setattr(profile, field, value)
            fields_to_update.append(field)
        else:
            print(f"[DEBUG] Field '{field}' does not exist on BusinessProfile model.")

    if not fields_to_update:
        return {"status": "error", "message": "No valid fields were provided for update."}

    try:
        # (The rest of your excellent debugging and saving logic is perfect and remains the same)
        print(f"[DEBUG] About to update fields {fields_to_update} with values {updates}")
        profile.save(update_fields=fields_to_update)
        print(f"[DEBUG] profile.save() called for fields: {fields_to_update}")
        
        return {
            "status": "success",
            "message": f"Successfully updated the following fields: {', '.join(fields_to_update)}",
            "updated_fields": fields_to_update
        }
    except Exception as e:
        print(f"[ERROR] Failed to save profile for user {user.id}: {e}")
        return {"status": "error", "message": f"An error occurred while saving: {e}"}

# ADD THE IMPORTS IN UTILS PY AFTER ADDING INFO ABOUT CHATBOT SET UP OR ANY PAGE TOO