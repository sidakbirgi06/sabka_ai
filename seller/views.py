from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import BusinessProfileStep1Form, BusinessProfileStep2Form, BusinessProfileStep3Form, BusinessProfileStep4Form, BusinessProfileStep5Form, ChatbotSettingsStep1Form, ChatbotSettingsStep2Form, ChatbotSettingsStep3Form
from .models import BusinessProfile, ChatbotSettings, Conversation, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SocialConnection
from .business_tools import get_entire_business_profile, update_business_profile
from google.ai.generativelanguage import Part




# Configure the generative AI model
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY")) # Or whatever name you are using

    # NEW: We are adding a system instruction to guide the AI
    system_instruction = (
        "You are a helpful and expert business assistant for a user who is already logged into the platform. "
        "When the user asks a question, your primary goal is to use your available tools to find the answer. "
        "You do not need to ask for the user's identity, ID, or name; the 'user' parameter for your tools will be provided automatically by the system based on their logged-in session. "
        "Formulate your final answers based on the output of the tools."
    )

    model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[get_entire_business_profile, update_business_profile],
    system_instruction=(
        "You are a helpful and intelligent business assistant for the 'Sabka Apna AI' platform. "
        "Your primary goal is to help the user manage their business profile by answering their questions and updating their information using the provided tools. "
        "The 'user' parameter for all tools will be provided automatically by the system. You must never ask the user for any kind of user ID."
        "\n\n"
        "**Communication Rules:**\n"
        "- Communicate in a friendly, professional, and concise manner.\n"
        "- NEVER mention that you are an AI or a language model.\n"
        "- CRITICALLY, NEVER reveal the names of the internal tools or functions you are using (e.g., 'get_entire_business_profile'). Frame all your responses naturally. If you can't do something, say 'I can't help with that right now,' not 'I don't have a tool for that.'\n"
        "\n\n"
        "**Tool Usage Rules:**\n"
        "- When the user asks to update information, be flexible. Map natural language to the correct database field names. For example, if the user says 'owners name', 'my name', or 'main contact', you should map this to the 'owner_name' field for the update tool.\n"
        "- Here are the available fields for the update tool to help you map them correctly: 'business_name', 'owner_name', 'contact_number', 'business_email', 'address', 'operating_hours', 'social_media_links', 'usp', 'target_market', 'audience_profile', 'product_categories', 'inventory_update_frequency', 'top_selling_products', 'combo_packs', 'return_policy', 'faqs'."
    )
)

except Exception as e:
    print(f"Error configuring Generative AI model: {e}")
    model = None




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

        # --- Connect to the AI ---
        load_dotenv()
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # This is the full history including the main prompt and past messages
            conversation_history_for_api = [
                {'role': 'user', 'parts': [system_prompt]},
                {'role': 'model', 'parts': ["Understood. I am ready to assist customers for " + profile.business_name]},
            ]
            for message in chat_history:
                api_role = 'model' if message.get('role') == 'bot' else 'user'
                conversation_history_for_api.append({'role': api_role, 'parts': message.get('parts')})
            
            chat_session = model.start_chat(history=conversation_history_for_api)
            response = chat_session.send_message(user_message)
            ai_message = response.text
            
            chat_history.append({'role': 'bot', 'parts': [ai_message]})

        except Exception as e:
            ai_message = f"An error occurred with the AI service: {e}"
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
                                chatbot_settings = ChatbotSettings.objects.get(user=user)
                                page_access_token = social_connection.page_access_token

                                # 2. Find or Create the Conversation record
                                # This is the "filing" step. Get the file for this customer, or create a new one.
                                conversation, created = Conversation.objects.get_or_create(
                                    social_connection=social_connection,
                                    customer_id=sender_id
                                )
                                # Optional: We could add logic here later to fetch the customer's name

                                # 3. Save the customer's incoming message
                                Message.objects.create(
                                    conversation=conversation,
                                    sender_type='customer',
                                    content=message_text
                                )


                                # (Existing AI Logic)
                                prompt = f"""
                                You are {chatbot_settings.chatbot_name}, a helpful AI assistant for {business_profile.business_name}.
                                Your persona should be: {chatbot_settings.chatbot_persona}.
                                Greet the user with: {chatbot_settings.greeting_message}.
                                
                                Here is the business information:
                                Business Name: {business_profile.business_name}
                                Description: {business_profile.business_description}
                                Product/Service Details: {business_profile.products_services}
                                FAQs: {business_profile.faqs}
                                Business Address: {business_profile.address}
                                Phone Number: {business_profile.phone_number}
                                Email: {business_profile.email}
                                Website: {business_profile.website}
                                Social Media Links: {business_profile.social_media_links}
                                Operating Hours: {business_profile.operating_hours}
                                Promotion/Deals: {business_profile.promotions_deals}
                                Return Policy: {business_profile.return_policy}
                                Shipping Info: {business_profile.shipping_info}
                                Payment Methods: {business_profile.payment_methods}
                                
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



tool_functions = {
    "get_entire_business_profile": get_entire_business_profile,
    "update_business_profile": update_business_profile,
}

# BUSINESS ASSISTANT API
@csrf_exempt
@login_required
def business_assistant_api(request):
    if not model:
        return JsonResponse({'error': 'AI model is not configured.'}, status=500)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Start a chat session
            chat = model.start_chat()
            
            # Send the first message to the AI
            response = chat.send_message(user_message)
            
            # Check if the AI wants to use a tool
            function_call = response.candidates[0].content.parts[0].function_call
            
            if function_call:
                # The AI wants to use a tool. Let's process it.
                tool_name = function_call.name
                tool_args = {key: value for key, value in function_call.args.items()}

                if tool_name in tool_functions:
                    selected_tool = tool_functions[tool_name]
                    tool_args['user'] = request.user
                    tool_output = selected_tool(**tool_args)
                    
                    function_response_part = Part(
                        function_response={
                            "name": tool_name,
                            "response": {"content": tool_output},
                        }
                    )
                    # We send this structured response back to the chat
                    response = chat.send_message(function_response_part)

            # The final reply from the AI ====
            bot_reply = response.text
            return JsonResponse({'reply': bot_reply})

        except Exception as e:
            print(f"Error in business_assistant_api: {e}")
            return JsonResponse({'error': f'An internal error occurred: {e}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)




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




