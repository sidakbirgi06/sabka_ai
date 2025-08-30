# in seller/context_processors.py

from .models import SocialConnection

def social_connections_context(request):
    # This function will run for every request.
    # We only want to run the database query if the user is logged in.
    if request.user.is_authenticated:
        facebook_connection = SocialConnection.objects.filter(user=request.user, platform='facebook').first()
        instagram_connection = SocialConnection.objects.filter(user=request.user, platform='instagram').first()
        
        # This dictionary gets added to the context of every template.
        return {
            'facebook_connection': facebook_connection,
            'instagram_connection': instagram_connection
        }
    
    # If the user is not logged in, return an empty dictionary.
    return {}