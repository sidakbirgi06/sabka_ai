from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import BusinessProfileStep1Form, BusinessProfileStep2Form, BusinessProfileStep3Form, BusinessProfileStep4Form, BusinessProfileStep5Form, ChatbotSettingsStep1Form, ChatbotSettingsStep2Form, ChatbotSettingsStep3Form
from .models import BusinessProfile, ChatbotSettings
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
from .models import FacebookPage
from .business_tools import get_business_info
from google.ai.generativelanguage import Part



# We have REMOVED the try/except block for debugging purposes
# genai.configure(api_key=os.environ.get("GOOGLE_API_KEY")) # Or the name you used
# model = genai.GenerativeModel(
#     model_name='gemini-1.5-flash',
#     tools=[get_business_info]
# )


# === FOR HOME PAGE ===
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


# ... your other views like home(), facebook_connect(), etc. ...

# WEBHOOK FUNCTION

@csrf_exempt
def webhook_view(request):
    # Handle the GET request for verification
    if request.method == 'GET':
        verify_token = os.environ.get('WEBHOOK_VERIFY_TOKEN')
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == verify_token:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('Error, invalid verification token', status=403)

    # Handle POST requests with incoming messages
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]      
                        recipient_id = messaging_event["recipient"]["id"]  
                        message_text = messaging_event["message"]["text"]  

                        try:
                            # Find the seller and their settings
                            facebook_page = FacebookPage.objects.get(page_id=recipient_id)
                            profile = facebook_page.user.businessprofile
                            settings = profile.chatbotsettings
                            page_access_token = facebook_page.page_access_token

                            # Integrate the "AI Brain"
                            system_prompt = f"""
                            You are an expert AI assistant for the business named '{profile.business_name}'.
                            Your assigned name is '{settings.ai_name}'. Your personality must be: '{settings.personality}'.
                            # ... (the rest of your long prompt is here) ...
                            ### FAQs ###
                            {profile.faqs}
                            """

                            load_dotenv()
                            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                            model = genai.GenerativeModel('gemini-1.5-flash-latest')

                            chat_session = model.start_chat(history=[])
                            response = chat_session.send_message(system_prompt + "\n\nCustomer message: " + message_text)
                            ai_reply = response.text

                            # Send the reply back to Facebook
                            send_facebook_message(sender_id, ai_reply, page_access_token)

                        except FacebookPage.DoesNotExist:
                            print(f"Received message for an unknown Page ID: {recipient_id}")
                            pass 
                        except Exception as e:
                            print(f"An error occurred: {e}")

        return HttpResponse(status=200)

    return HttpResponse("Unsupported method", status=405)


@login_required
def debug_view(request):
    all_profiles = BusinessProfile.objects.all()
    context = {
        'profiles': all_profiles
    }
    return render(request, 'seller/debug_data.html', context)






def facebook_connect(request):
    APP_ID = os.environ.get('FACEBOOK_APP_ID')
    redirect_uri = request.build_absolute_uri(reverse('facebook_callback'))
    scope = 'pages_show_list,pages_messaging,public_profile'
    
    auth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code"
    )
    
    return redirect(auth_url)



# def facebook_callback(request):
#     # 1. Get the temporary 'code' from the URL
#     code = request.GET.get('code')
#     if not code:
#         # Handle the error case where the user denied permission or something went wrong
#         return redirect('dashboard') # Redirect to dashboard or an error page

#     # 2. Exchange the code for a user access token
#     APP_ID = os.environ.get('FACEBOOK_APP_ID')
#     APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
#     redirect_uri = request.build_absolute_uri(reverse('facebook_callback'))

#     token_url = (
#         f"https://graph.facebook.com/v19.0/oauth/access_token?"
#         f"client_id={APP_ID}&"
#         f"redirect_uri={redirect_uri}&"
#         f"client_secret={APP_SECRET}&"
#         f"code={code}"
#     )

#     response = requests.get(token_url)
#     user_token_data = response.json()
#     user_access_token = user_token_data.get('access_token')

#     if not user_access_token:
#         # Handle error: couldn't get the token
#         return redirect('dashboard')

#     # 3. Get the list of pages the user manages
#     pages_url = f"https://graph.facebook.com/me/accounts?access_token={user_access_token}"
#     response = requests.get(pages_url)
#     pages_data = response.json()

#     # For simplicity, we'll use the first page in the list.
#     if pages_data and 'data' in pages_data and len(pages_data['data']) > 0:
#         page_info = pages_data['data'][0]
#         page_id = page_info['id']
#         page_name = page_info['name']
#         page_access_token = page_info['access_token']

#         # 4. Save the connection details to the database
#         FacebookPage.objects.update_or_create(
#             user=request.user,
#             defaults={
#                 'page_id': page_id,
#                 'page_name': page_name,
#                 'page_access_token': page_access_token
#             }
#         )

#     # 5. Redirect to a success page or the dashboard
#     # ---- IMPORTANT: Change this to your actual dashboard URL name ----
#     return redirect('dashboard')




def facebook_callback(request):
    # 1. Get the temporary 'code' from the URL
    code = request.GET.get('code')
    if not code:
        # Handle the error case where the user denied permission or something went wrong
        return redirect('home')  # Redirect to home or an error page

    # 2. Exchange the code for a user access token
    APP_ID = os.environ.get('FACEBOOK_APP_ID')
    APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
    redirect_uri = request.build_absolute_uri(reverse('facebook_callback'))

    token_url = (
        f"https://graph.facebook.com/v19.0/oauth/access_token?"
        f"client_id={APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"client_secret={APP_SECRET}&"
        f"code={code}"
    )

    response = requests.get(token_url)
    user_token_data = response.json()
    user_access_token = user_token_data.get('access_token')

    if not user_access_token:
        
        # Handle error: couldn't get the token
        print("Error: could not get user access token:", user_token_data)
        return redirect('home')

    # 3. Get the list of pages the user manages
    pages_url = f"https://graph.facebook.com/me/accounts?access_token={user_access_token}"
    response = requests.get(pages_url)
    pages_data = response.json()

    if not pages_data or 'data' not in pages_data or len(pages_data['data']) == 0:
        print("Error: no managed pages found:", pages_data)
        return redirect('home')

    # For simplicity, we'll use the first page in the list.
    page_info = pages_data['data'][0]
    page_id = page_info['id']
    page_name = page_info['name']
    page_access_token = page_info['access_token']

    # 4. Save the connection details to the database
    facebook_page, created = FacebookPage.objects.update_or_create(
        user=request.user,
        defaults={
            'page_id': page_id,
            'page_name': page_name,
            'page_access_token': page_access_token
        }
    )

    # 5. Subscribe the page to your webhook
    subscribe_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
    params = {
        "subscribed_fields": "messages,messaging_postbacks",
        "access_token": page_access_token
    }
    subscribe_response = requests.post(subscribe_url, params=params)

    print("Subscribe response:", subscribe_response.status_code, subscribe_response.text)

    # 6. Redirect to home (or success page)
    return redirect('home')


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
        tools=[get_business_info],
        system_instruction=system_instruction  # <-- We add the instruction here
    )
except Exception as e:
    print(f"Error configuring Generative AI model: {e}")
    model = None



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

            # This is our library of available tools
            tool_library = {
                "get_business_info": get_business_info
            }

            # Start a chat session WITHOUT automatic function calling
            chat = model.start_chat()
            
            # Send the initial message
            response = chat.send_message(user_message)
            
            # Check if the model wants to call a function
            function_call = response.candidates[0].content.parts[0].function_call
            
            while function_call:
                function_name = function_call.name
                function_to_call = tool_library.get(function_name)
                
                if function_to_call:
                    # --- THIS IS THE CRUCIAL PART ---
                    # We manually call the function and pass in the logged-in user
                    function_response = function_to_call(user=request.user)
                    
                    # Send the tool's output back to the model
                    response = chat.send_message(
                        Part(function_response={
                            "name": function_name,
                            "response": {
                                # The tool returns a string, so we package it as "result"
                                "result": function_response 
                            },
                        })
                    )
                    # Check if the model wants to call another function
                    function_call = response.candidates[0].content.parts[0].function_call
                else:
                    # If the model tries to call a function we don't have, break the loop
                    break

            bot_reply = response.text
            return JsonResponse({'reply': bot_reply})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error in business_assistant_api: {e}")
            return JsonResponse({'error': 'An internal error occurred.'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def business_assistant_page(request):
    # This comment is here to ensure the file is updated
    return render(request, 'seller/business_assistant_page.html')

