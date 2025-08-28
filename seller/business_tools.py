# in seller/business_tools.py

from .models import BusinessProfile

def get_business_info(user):
    """
    Retrieves the business profile information for a given user.
    Returns a dictionary with the info or an error message string.
    """
    try:
        # Find the business profile linked to the logged-in user
        profile = BusinessProfile.objects.get(user=user)
        
        # Prepare the information using the CORRECT field names from models.py
        info_string = (
            f"Business Name: {profile.business_name}\n"
            f"Owner Name: {profile.owner_name}\n"
            f"Description: {profile.description}\n"  # <-- FIXED
            f"Address: {profile.address}\n"
            f"Phone Number: {profile.contact_number}" # <-- FIXED
        )
        return info_string

    except BusinessProfile.DoesNotExist:
        return "It looks like you haven't set up your business profile yet. Please complete your profile first."
    
    except Exception as e:
        # This is our user-friendly final error message
        print(f"Error in get_business_info: {e}")
        return "Sorry, an unexpected error occurred while trying to retrieve your business information."