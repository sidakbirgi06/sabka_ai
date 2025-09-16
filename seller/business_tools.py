import json
from django.contrib.auth.models import User
from .models import BusinessProfile

def get_business_profile_field(user_id: int, field_name: str) -> str:
    """
    Fetches the value of a single, specific field from the user's business profile.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)
        
        if hasattr(profile, field_name):
            value = getattr(profile, field_name)
            return json.dumps({"status": "success", "field": field_name, "value": value})
        else:
            return json.dumps({"status": "error", "message": f"Field '{field_name}' does not exist."})

    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return json.dumps({"status": "error", "message": "Profile not found for this user."})

def update_business_profile_field(user_id: int, field_name: str, new_value: str) -> str:
    """
    Updates a single, specific field in the user's business profile with a new value.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)

        if hasattr(profile, field_name):
            setattr(profile, field_name, new_value)
            profile.save(update_fields=[field_name]) # Safe save
            return json.dumps({"status": "success", "message": f"Field '{field_name}' was updated."})
        else:
            return json.dumps({"status": "error", "message": f"Field '{field_name}' does not exist."})

    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return json.dumps({"status": "error", "message": "Profile not found for this user."})