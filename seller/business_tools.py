import json
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .models import BusinessProfile

# --- TOOL 1: FOR READING DATA ---
# This tool reliably reads ALL fields from your profile.
def get_entire_business_profile(user_id: int) -> str:
    """
    Fetches all business profile fields for a given user ID and returns them as a JSON string.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)
        
        # This is the reliable Django method to get all model fields.
        profile_data = model_to_dict(profile)

        # Remove internal fields the AI doesn't need.
        profile_data.pop('id', None)
        profile_data.pop('user', None)

        return json.dumps(profile_data, indent=2)

    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return json.dumps({"error": "Profile not found for this user."})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})


# --- TOOL 2: FOR WRITING DATA ---
# This tool safely updates ONLY the specified fields in your profile.
def update_business_profile(user_id: int, **updates) -> str:
    """
    Updates one or more fields in the BusinessProfile for a given user ID.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)
        
        updated_fields = list(updates.keys())
        if not updated_fields:
            return json.dumps({"success": False, "error": "No valid fields provided to update."})

        for field, value in updates.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        # This is the crucial fix to prevent silent save failures.
        profile.save(update_fields=updated_fields)
        
        return json.dumps({"success": True, "message": f"Profile updated successfully for fields: {updated_fields}"})
            
    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return json.dumps({"success": False, "error": "Profile not found for this user."})
    except Exception as e:
        return json.dumps({"success": False, "error": f"An unexpected error occurred: {str(e)}"})