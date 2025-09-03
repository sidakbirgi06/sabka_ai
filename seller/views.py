from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import BusinessProfileStep1Form, BusinessProfileStep2Form, BusinessProfileStep3Form, BusinessProfileStep4Form, BusinessProfileStep5Form, ChatbotSettingsStep1Form, ChatbotSettingsStep2Form, ChatbotSettingsStep3Form
from .models import BusinessProfile, ChatbotSettings, Conversation, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os
from dotenv import load_dotenv
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SocialConnection
from google.ai.generativelanguage import Part
from .ai_utils import get_gemini_response, get_assistant_response
from django.shortcuts import get_object_or_404
import google.generativeai as genai

import logging




# FOR HOME PAGE 
def home(request):
    return render(request, 'seller/home.html')

# FOR SIGNUP PAGE
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'seller/signup.html', {'form': form})

# LOGIN AND LOGOUT
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Log in the user
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'seller/login.html', {'form': form})

# Our new logout view
@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    
# BUSINESS INFO PAGE SECTION 1
@login_required
def business_info_step1(request):
    try:
        profile = request.user.businessprofile
    except BusinessProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = BusinessProfileStep1Form(request.POST, instance=profile)
        if form.is_valid():
            new_profile = form.save(commit=False)
            new_profile.user = request.user
            new_profile.save()
            return redirect('business_info_step2')
    else:
        form = BusinessProfileStep1Form(instance=profile)

    return render(request, 'seller/business_info_step1.html', {'form': form})

# BUSINESS INFO PAGE SECITON 2
@login_required
def business_info_step2(request):
    profile = request.user.businessprofile
    if request.method == 'POST':
        form = BusinessProfileStep2Form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('business_info_step3')
    else:
        form = BusinessProfileStep2Form(instance=profile)

    return render(request, 'seller/business_info_step2.html', {'form': form})

# BUSINESS INFO PAGE SECTION 3
@login_required
def business_info_step3(request):
    profile = request.user.businessprofile
    if request.method == 'POST':
        form = BusinessProfileStep3Form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('business_info_step4')
    else:
        form = BusinessProfileStep3Form(instance=profile)

    return render(request, 'seller/business_info_step3.html', {'form': form})

#BUSINESS INFO PAGE SECTION 4
@login_required
def business_info_step4(request):
    profile = request.user.businessprofile
    if request.method == 'POST':
        form = BusinessProfileStep4Form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('business_info_step5')
    else:
        form = BusinessProfileStep4Form(instance=profile)

    return render(request, 'seller/business_info_step4.html', {'form': form})

#BUSINESS INFO PAGE SECTION 5
@login_required
def business_info_step5(request):
    profile = request.user.businessprofile
    if request.method == 'POST':
        form = BusinessProfileStep5Form(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BusinessProfileStep5Form(instance=profile)

    return render(request, 'seller/business_info_step5.html', {'form': form})

#CHATBOT SETUP PAGES

# CHATBOT SETUP PAGE 1
@login_required
def chatbot_setup_step1(request):
    profile = request.user.businessprofile
    settings, created = ChatbotSettings.objects.get_or_create(business_profile=profile)

    if request.method == 'POST':
        form = ChatbotSettingsStep1Form(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('chatbot_setup_step2')
    else:
        form = ChatbotSettingsStep1Form(instance=settings)

    return render(request, 'seller/chatbot_setup_step1.html', {'form': form})

#CHATBOT SETUP PAGE 2
@login_required
def chatbot_setup_step2(request):
    profile = request.user.businessprofile
    settings = profile.chatbotsettings # Get the settings linked to the profile
    if request.method == 'POST':
        form = ChatbotSettingsStep2Form(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            # For now, we redirect to home. Later this will go to step 3.
            return redirect('chatbot_setup_step3')
    else:
        form = ChatbotSettingsStep2Form(instance=settings)

    return render(request, 'seller/chatbot_setup_step2.html', {'form': form})

#CHATBOT SETUP PAGE 3
@login_required
def chatbot_setup_step3(request):
    profile = request.user.businessprofile
    settings = profile.chatbotsettings
    if request.method == 'POST':
        form = ChatbotSettingsStep3Form(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            # After the final step, redirect to the main dashboard.
            return redirect('dashboard')
    else:
        form = ChatbotSettingsStep3Form(instance=settings)

    return render(request, 'seller/chatbot_setup_step3.html', {'form': form})

# DASHBOARD
@login_required
def dashboard(request):
    try:
        profile = request.user.businessprofile
    except BusinessProfile.DoesNotExist:
        profile = None

    context = {
        'profile': profile
    }
    return render(request, 'seller/dashboard.html', context)

# INBOX
@login_required
def inbox(request):
    return render(request, 'seller/inbox.html')

# CHAT VIEW
@login_required
def chat_view(request):
    try:
        profile = request.user.businessprofile
        settings = profile.chatbotsettings
    except (BusinessProfile.DoesNotExist, ChatbotSettings.DoesNotExist):
        return render(request, 'seller/chat.html', {'error': "Please complete your Business Profile and Chatbot Setup first."})

    # This line clears the chat history when you add "?new=true" to the URL
    if 'new' in request.GET:
        if 'chat_history' in request.session:
            del request.session['chat_history']
        return redirect('chat_view')

    # --- The Upgraded System Prompt (Briefing Document) ---
    system_prompt = f"""
    You are an expert AI assistant for the business named '{profile.business_name}'.
    Your assigned name is '{settings.ai_name}'. Your personality must be: '{settings.personality}'.

    ### CORE INSTRUCTIONS ###
    1. Your primary goal is to answer customer questions based ONLY on the information provided in the following sections.
    2. First, look for an answer in the 'FREQUENTLY ASKED QUESTIONS (FAQs)' section.
    3. If the answer is not in the FAQs, use the information from the other sections.
    4. If you cannot find an answer anywhere in the provided information, you MUST follow this strategy: {settings.get_error_handling_strategy_display()}. If a custom reply is needed, use this one: '{settings.custom_error_reply}'.
    5. Adhere to your personality traits: Greet new customers with '{settings.greeting}'. {'You MUST use emojis.' if settings.use_emojis else 'Do not use emojis.'} Your signature closing line is '{settings.signature_line}'. You must NEVER use these words or phrases: '{settings.phrases_to_avoid}'.

    ### BUSINESS OVERVIEW ###
    - Business Name: {profile.business_name}
    - Owner's Name: {profile.owner_name}
    - Description: {profile.description}
    - Contact: Phone: {profile.contact_number}, Email: {profile.business_email}
    - Address / Location: {profile.address}
    - Operating Hours: {profile.operating_hours}

    ### PRODUCT INFORMATION ###
    - Product Categories: {profile.product_categories}
    - Top-Selling Products / New Arrivals: {profile.top_selling_products}
    - Special Combos or Deals: {profile.combo_packs}

    ### POLICIES & LOGISTICS ###
    - Payment Methods: You accept Cash on Delivery ({'Yes' if profile.accepts_cod else 'No'}), UPI ({'Yes' if profile.accepts_upi else 'No'}), and Card ({'Yes' if profile.accepts_card else 'No'}).
    - Delivery Methods: {profile.delivery_methods}
    - Return/Refund Policy: {profile.return_policy}

    ### FREQUENTLY ASKED QUESTIONS (FAQs) ###
    {profile.faqs}
    """

    # --- Manage Chat History using Django Sessions ---
    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.POST.get('message')
        chat_history.append({'role': 'user', 'parts': [user_message]})

        # --- Connect to the AI (Definitive Stateless Method) ---
        try:
            # Build the conversation history ONLY from the actual chat messages
            conversation_history_for_api = []
            for message in chat_history:
                api_role = 'model' if message.get('role') == 'bot' else 'user'
                conversation_history_for_api.append({'role': api_role, 'parts': message.get('parts')})

            # Configure the model
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

            # *** THE KEY FIX IS HERE ***
            # We pass the system_prompt to its own dedicated parameter
            model = genai.GenerativeModel(
                'gemini-1.5-flash-latest',
                system_instruction=system_prompt  # <-- Use the correct parameter
            )

            # Generate content using ONLY the conversational history
            response = model.generate_content(conversation_history_for_api)
            
            ai_message = response.text
            chat_history.append({'role': 'bot', 'parts': [ai_message]})

        except Exception as e:
            print(f"AI Generation Error: {e}") # For server logs
            ai_message = f"An error occurred with the AI service. Please try again."
            chat_history.append({'role': 'bot', 'parts': [ai_message]})

        request.session['chat_history'] = chat_history
        return redirect('chat_view')

    context = {'chat_history': chat_history}
    return render(request, 'seller/chat.html', context)




# HELPER FUNCTION TO SEND MESSAGES
def send_facebook_message(recipient_id, message_text, page_access_token):
    """
    Sends a text message to a user on Facebook Messenger.
    """
    params = {
        "access_token": page_access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        },
        "messaging_type": "RESPONSE"
    })
    
    # Make the API call to the Facebook Graph API
    response = requests.post(
        "https://graph.facebook.com/v19.0/me/messages",
        params=params,
        headers=headers,
        data=data
    )
    
    # Optional: Print the response from Facebook to see if it was successful
    print(f"Facebook API Response: {response.status_code}, {response.text}")



# WEBHOOK FUNCTION
@csrf_exempt
def webhook_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get('object') == 'page' or data.get('object') == 'instagram':
            for entry in data.get('entry', []):
                # Determine platform and get messaging events
                if 'messaging' in entry: # Facebook
                    messaging_events = entry.get('messaging', [])
                    platform = 'facebook'
                elif 'standby' in entry: # Instagram (sometimes uses standby)
                    messaging_events = entry.get('standby', [])
                    platform = 'instagram'
                else:
                    continue

                for event in messaging_events:
                    if event.get('message'):
                        sender_id = event['sender']['id']
                        recipient_id = event['recipient']['id']
                        message_text = event['message'].get('text')

                        if message_text:
                            try:

                                # 1. Find the SocialConnection for this page/profile
                                if platform == 'facebook':
                                    social_connection = SocialConnection.objects.get(page_id=recipient_id, platform='facebook')
                                elif platform == 'instagram':
                                    social_connection = SocialConnection.objects.get(page_id=recipient_id, platform='instagram')
                                else:
                                    continue # Skip if platform is unknown

                                user = social_connection.user
                                business_profile = BusinessProfile.objects.get(user=user)
                                chatbot_settings = ChatbotSettings.objects.get(business_profile=business_profile)
                                page_access_token = social_connection.page_access_token

                                # 2. Find or Create the Conversation record
                                # This is the "filing" step. Get the file for this customer, or create a new one.
                                conversation, created = Conversation.objects.get_or_create(
                                    social_connection=social_connection,
                                    customer_id=sender_id
                                )
                                if created:
                                    customer_name = get_facebook_user_profile(sender_id, page_access_token)
                                    conversation.customer_name = customer_name
                                    conversation.save()

                                # 3. Save the customer's incoming message
                                Message.objects.create(
                                    conversation=conversation,
                                    sender_type='customer',
                                    content=message_text
                                )


                                # (Existing AI Logic)
                                prompt = f"""
                                You are {chatbot_settings.ai_name}, a helpful AI assistant for {business_profile.business_name}.
                                Your persona should be: {chatbot_settings.personality}.
                                Greet the user with: {chatbot_settings.greeting}.
                                
                                Here is the business information:
                                Business Name: {business_profile.business_name}
                                Description: {business_profile.description}
                                Product/Service Details: {business_profile.product_categories}
                                FAQs: {business_profile.faqs}
                                Business Address: {business_profile.address}
                                Phone Number: {business_profile.contact_number}
                                Email: {business_profile.business_email}
                                Social Media Links: {business_profile.social_media_links}
                                Operating Hours: {business_profile.operating_hours}
                                Return Policy: {business_profile.return_policy}
                                Delvery Info: {business_profile.delivery_methods}
                                Payment Methods: {business_profile.accepts_card}
                                Payment Methods: {business_profile.accepts_cod}
                                Payment Methods: {business_profile.accepts_upi}
                                
                                A customer has sent the following message: "{message_text}"
                                
                                Please provide a helpful and in-character response.
                                """

                                ai_response = get_gemini_response(prompt)


                                # 4. Save the AI's outgoing reply
                                Message.objects.create(
                                    conversation=conversation,
                                    sender_type='ai',
                                    content=ai_response
                                )
                                

                                # (Existing Sending Logic)
                                if platform == 'facebook':
                                    send_facebook_message(sender_id, ai_response, page_access_token)
                                elif platform == 'instagram':
                                    # Assuming you have a similar function for Instagram or it uses the same one
                                    send_facebook_message(sender_id, ai_response, page_access_token)

                            except SocialConnection.DoesNotExist:
                                print(f"Warning: Received message for untracked page/profile ID: {recipient_id}")
                            except Exception as e:
                                print(f"An error occurred: {e}")

        return HttpResponse(status=200)
    return HttpResponse(status=403)


@login_required
def debug_view(request):
    all_profiles = BusinessProfile.objects.all()
    context = {
        'profiles': all_profiles
    }
    return render(request, 'seller/debug_data.html', context)



# BUSINESS ASSISTANT PAGE
def business_assistant_page(request):
    # This comment is here to ensure the file is updated
    return render(request, 'seller/business_assistant_page.html')


# BUSINESS ASSISTANT API
@login_required
@csrf_exempt
def business_assistant_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # SINGLE, CLEAN CALL TO OUR NEW UTILITY FUNCTION
            # We pass the message and the logged-in user object
            ai_reply = get_assistant_response(user_message=user_message, user_object=request.user)

            return JsonResponse({'reply': ai_reply})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error in business_assistant_api view: {e}")
            return JsonResponse({'error': 'An internal error occurred'}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)




@login_required
def facebook_connect(request):
    app_id = os.environ.get('FACEBOOK_APP_ID')
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    scope = 'pages_show_list,pages_messaging,public_profile'
    state = 'facebook_flow' # We add a 'state' to know this is for Facebook
    
    auth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={app_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"state={state}"
    )
    return redirect(auth_url)


@login_required
def instagram_connect(request):
    app_id = os.environ.get('FACEBOOK_APP_ID')
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    scope = 'instagram_basic,instagram_manage_messages,pages_show_list'
    state = 'instagram_flow'

    auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&response_type=code"
        f"&state={state}"
    )
    return redirect(auth_url)


# in seller/views.py

# This is the single, unified callback view for both platforms (FINAL CORRECTED VERSION)
def oauth_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state') # Get the state to check the platform

    if not code:
        return redirect('home')

    # Step 1: Exchange code for a user access token
    APP_ID = os.environ.get('FACEBOOK_APP_ID')
    APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    
    token_url = f"https://graph.facebook.com/v19.0/oauth/access_token?client_id={APP_ID}&redirect_uri={redirect_uri}&client_secret={APP_SECRET}&code={code}"
    response = requests.get(token_url)
    user_token_data = response.json()
    user_access_token = user_token_data.get('access_token')

    if not user_access_token:
        print("Error getting user access token:", user_token_data)
        return redirect('home')

    # Step 2: Get the list of pages/accounts the user manages
    accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?fields=instagram_business_account,name,access_token&access_token={user_access_token}"
    response = requests.get(accounts_url)
    pages_data = response.json()
    
    page_id, page_name, page_access_token, platform_to_save = (None, None, None, None)

    # Step 3: Find the correct page/account based on the flow (Facebook or Instagram)
    if state == 'instagram_flow':
        platform_to_save = 'instagram'
        if 'data' in pages_data:
            for page in pages_data['data']:
                if 'instagram_business_account' in page:
                    ig_account_info = page['instagram_business_account']
                    page_id = ig_account_info['id']
                    page_name = ig_account_info.get('username', 'Instagram Account')
                    page_access_token = page['access_token']
                    break
        if not page_id:
            print("Error: No Instagram Business Account found linked to any Facebook Page.")
            return redirect('home')
    
    else: # Default to Facebook flow
        platform_to_save = 'facebook'
        if not pages_data or 'data' not in pages_data or len(pages_data['data']) == 0:
            print("Error: no managed Facebook pages found:", pages_data)
            return redirect('home')
        page_info = pages_data['data'][0]
        page_id = page_info['id']
        page_name = page_info['name']
        page_access_token = page_info['access_token']

    # Step 4: Save the connection details to our database
    if page_id and platform_to_save:
        SocialConnection.objects.update_or_create(
            user=request.user,
            platform=platform_to_save,
            defaults={ 'page_id': page_id, 'page_name': page_name, 'page_access_token': page_access_token }
        )

        # --- STEP 5: THIS IS THE NEW, CRUCIAL PART ---
        # Subscribe this specific page/account to our app's webhook
        subscribe_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
        params = {
            "subscribed_fields": "messages",
            "access_token": page_access_token
        }
        subscribe_response = requests.post(subscribe_url, params=params)
        print(f"Subscribed {page_name} ({platform_to_save}) to webhooks: {subscribe_response.status_code}, {subscribe_response.text}")

    return redirect('home')



#TO GET PROFILE OF USER
def get_facebook_user_profile(user_id, page_access_token):
    """
    Fetches a user's first and last name from the Meta Graph API.
    """
    # The URL for the Graph API request
    url = f"https://graph.facebook.com/v19.0/{user_id}" # Using a recent, stable API version
    
    # The parameters for the request
    params = {
        'fields': 'first_name,last_name',
        'access_token': page_access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        # Combine the names into a full name
        full_name = f"{first_name} {last_name}".strip()
        
        # Return the full name, or the user_id as a fallback if the name is blank
        return full_name if full_name else user_id

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Facebook user profile for ID {user_id}: {e}")
        # If the API call fails, just return the user_id as a fallback
        return user_id
    


# INBOX PAGE
@login_required
def inbox_list_view(request):
    """
    Fetches and displays the list of all conversations for the logged-in user.
    """
    # Find all conversations linked to the social connections of the currently logged-in user
    conversations = Conversation.objects.filter(
        social_connection__user=request.user
    ).order_by('-updated_at') # Order by most recently updated

    context = {
        'conversations': conversations
    }
    return render(request, 'seller/inbox.html', context)


# TO VIEW SPECIFIC MSG FROM INBOX PAGE
@login_required
def inbox_detail_view(request, conversation_id):
    """
    Fetches and displays the messages for a single, specific conversation.
    """
    # Get the specific conversation, but also ensure it belongs to the logged-in user for security
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        social_connection__user=request.user
    )
    
    # Get all messages related to this conversation (they are already ordered by timestamp)
    messages = conversation.messages.all()

    context = {
        'conversation': conversation,
        'messages': messages,
    }
    return render(request, 'seller/conversation_detail.html', context)




