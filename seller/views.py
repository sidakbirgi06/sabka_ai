from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import BusinessProfileStep1Form, BusinessProfileStep2Form, BusinessProfileStep3Form, BusinessProfileStep4Form, BusinessProfileStep5Form, ChatbotSettingsStep1Form, ChatbotSettingsStep2Form, ChatbotSettingsStep3Form
from .models import BusinessProfile, ChatbotSettings
from django.contrib.auth.decorators import login_required
import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

# FOR HOME PAGE
# @login_required
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
    # We find the business profile that is linked to the currently logged-in user
    try:
        profile = request.user.businessprofile
    except BusinessProfile.DoesNotExist:
        profile = None # This handles the case where a new user hasn't created a profile yet

    context = {
        'profile': profile
    }

    return render(request, 'seller/dashboard.html', context)

# INBOX
@login_required
def inbox(request):
    return render(request, 'seller/inbox.html')

# CHAT VIEW
# in seller/views.py

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


# This function sends a reply back to the user on Facebook Messenger
def send_facebook_message(recipient_id, message_text):
    page_access_token = os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')
    params = { "access_token": page_access_token }
    headers = { "Content-Type": "application/json" }
    data = {
        "recipient": { "id": recipient_id },
        "message": { "text": message_text },
        "messaging_type": "RESPONSE"
    }
    # We are using v19.0 of the Graph API
    r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
    if r.status_code != 200:
        # We print any errors to the Render logs for debugging
        print(f"Error sending message: {r.status_code} {r.text}")


#WEBHOOK VIEW
@csrf_exempt
def webhook_view(request):
    # Handle the one-time verification GET request from Meta
    if request.method == 'GET':
        verify_token = os.environ.get('WEBHOOK_VERIFY_TOKEN')
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == verify_token:
            print('WEBHOOK_VERIFIED')
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('Error, invalid verification token', status=403)

    # Handle incoming messages (POST requests) from users
    if request.method == 'POST':
        data = json.loads(request.body)
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]      # User's ID on Facebook
                        message_text = messaging_event["message"]["text"]  # The message they sent

                        # --- THIS IS THE NEW LOGIC ---
                        try:
                            # For our prototype, we'll just use the first business profile we find.
                            # A real multi-user app would need a more complex way to find the right profile.
                            profile = BusinessProfile.objects.first()
                            settings = profile.chatbotsettings

                            # 1. Build the System Prompt (the "Briefing Document")
                            system_prompt = f"""
                            You are an expert AI assistant for the business named '{profile.business_name}'.
                            Your assigned name is '{settings.ai_name}'. Your personality must be: '{settings.personality}'.

                            ### CORE INSTRUCTIONS ###
                            1. Your primary goal is to answer customer questions based ONLY on the information provided below.
                            2. First, try to find an answer in the 'FAQs' section.
                            3. If not in the FAQs, use the other business information.
                            4. Adhere to your personality traits: Greet new customers with '{settings.greeting}'. {'You MUST use emojis.' if settings.use_emojis else 'Do not use emojis.'} Your signature closing line is '{settings.signature_line}'. You must NEVER use these words or phrases: '{settings.phrases_to_avoid}'.

                            ### BUSINESS INFORMATION ###
                            - Description: {profile.description}
                            - Contact: Phone: {profile.contact_number}, Email: {profile.business_email}
                            - Address / Location: {profile.address}
                            - Operating Hours: {profile.operating_hours}
                            - Product Categories: {profile.product_categories}
                            - Top-Selling Products: {profile.top_selling_products}
                            - Deals/Combos: {profile.combo_packs}
                            - Payment Methods: COD: {'Yes' if profile.accepts_cod else 'No'}, UPI: {'Yes' if profile.accepts_upi else 'No'}, Card: {'Yes' if profile.accepts_card else 'No'}
                            - Delivery Methods: {profile.delivery_methods}
                            - Return/Refund Policy: {profile.return_policy}

                            ### FAQs ###
                            {profile.faqs}
                            """

                            # 2. Connect to the AI and get a response
                            load_dotenv()
                            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                            model = genai.GenerativeModel('gemini-1.5-flash-latest')

                            conversation_history_for_api = [
                                {'role': 'user', 'parts': [system_prompt]},
                                {'role': 'model', 'parts': ["Understood. I am ready to assist customers for " + profile.business_name]},
                            ]

                            chat_session = model.start_chat(history=conversation_history_for_api)
                            response = chat_session.send_message(message_text)
                            ai_reply = response.text

                            # 3. Send the AI's reply back to the user on Facebook
                            send_facebook_message(sender_id, ai_reply)

                        except Exception as e:
                            print(f"Error processing message: {e}")
                            # Send a fallback message if our AI logic fails
                            send_facebook_message(sender_id, "Sorry, I'm having a little trouble right now. A human will be with you shortly.")

        # We must return a 200 OK to Facebook to show we received the message.
        return HttpResponse(status=200)

    return HttpResponse("Unsupported method", status=405)