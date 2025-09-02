from django.urls import path
from . import views

# in seller/urls.py

urlpatterns = [
    path('', views.home, name='home'),

    path('signup/', views.signup, name='signup'),

    path('login/', views.login_view, name='login'), 

    path('logout/', views.logout_view, name='logout'),

    path('business-info/step-1/', views.business_info_step1, name='business_info_step1'),
    path('business-info/step-2/', views.business_info_step2, name='business_info_step2'),
    path('business-info/step-3/', views.business_info_step3, name='business_info_step3'),
    path('business-info/step-4/', views.business_info_step4, name='business_info_step4'),
    path('business-info/step-5/', views.business_info_step5, name='business_info_step5'),

    path('chatbot-setup/step-1/', views.chatbot_setup_step1, name='chatbot_setup_step1'),
    path('chatbot-setup/step-2/', views.chatbot_setup_step2, name='chatbot_setup_step2'),
    path('chatbot-setup/step-3/', views.chatbot_setup_step3, name='chatbot_setup_step3'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('inbox/', views.inbox, name='inbox'),

    path('chat/', views.chat_view, name='chat_view'),

    path('webhook/', views.webhook_view, name='webhook'),
    
    path('debug-data/', views.debug_view, name='debug_data'),
    
    # Connection URLs
    path('connect/facebook/', views.facebook_connect, name='facebook_connect'),
    path('connect/instagram/', views.instagram_connect, name='instagram_connect'),
    
    # Single, Unified Callback URL
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),

    # Business Assistant URLs
    path('business-assistant/', views.business_assistant_page, name='business_assistant_page'),
    path('api/business-assistant-chat/', views.business_assistant_api, name='business_assistant_api'),


    # for inbox
    path('inbox/', views.inbox_list_view, name='inbox_list'),

    #for a single specific chat in inbox
    path('inbox/<int:conversation_id>/', views.inbox_detail_view, name='inbox_detail'),




]