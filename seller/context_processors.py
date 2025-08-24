# In seller/context_processors.py

from .models import FacebookPage

def connection_status(request):
    # Default to False if the user is not even logged in
    if not request.user.is_authenticated:
        return {'is_connected': False}
    
    # If they are logged in, check the database for a connection
    is_connected = FacebookPage.objects.filter(user=request.user).exists()
    return {'is_connected': is_connected}