import json
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .models import BusinessProfile
from enum import Enum


class ProfileAction(Enum):
    READ = "READ"
    WRITE = "WRITE"


def manage_business_profile(
    user_id: int,
    action: ProfileAction,
    # All updatable fields from your model are listed here
    business_name: str = None, description: str = None, owner_name: str = None,
    contact_number: str = None, business_email: str = None, address: str = None,
    operating_hours: str = None, social_media_links: str = None, usp: str = None,
    target_market: str = None, audience_profile: str = None, product_categories: str = None,
    inventory_update_frequency: str = None, top_selling_products: str = None,
    combo_packs: str = None, accepts_cod: bool = None, accepts_upi: bool = None,
    accepts_card: bool = None, delivery_methods: str = None, return_policy: str = None,
    faqs: str = None
) -> str:
    """
    Manages the user's business profile.
    Use action='READ' to fetch the complete profile.
    Use action='WRITE' to update specific fields by providing them as arguments.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = BusinessProfile.objects.get(user=user)

        # ----------------- READ -----------------
        if action == ProfileAction.READ:
            profile_data = model_to_dict(profile)
            profile_data.pop('id', None)
            profile_data.pop('user', None)
            return json.dumps({"status": "success", "data": profile_data})

        # ----------------- WRITE -----------------
        elif action == ProfileAction.WRITE:
            updates = {}
            # Only include actual DB fields (skip id/user)
            model_fields = [f.name for f in profile._meta.fields if f.name not in ['id', 'user']]

            for field in model_fields:
                value = locals().get(field)
                if value is not None:
                    updates[field] = value

            if not updates:
                return json.dumps({
                    "status": "error",
                    "message": "No valid fields were provided for update."
                })

            for field, value in updates.items():
                setattr(profile, field, value)

            # Save only updated fields
            profile.save(update_fields=list(updates.keys()))

            return json.dumps({
                "status": "success",
                "message": f"Successfully updated fields: {list(updates.keys())}"
            })

    except (User.DoesNotExist, BusinessProfile.DoesNotExist):
        return json.dumps({"status": "error", "message": "Profile not found."})
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        })
