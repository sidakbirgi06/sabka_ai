import os
import google.generativeai as genai 
import traceback
import json
import requests
from .business_tools import get_business_profile_field, update_business_profile_field




# FOR CHATBOT IN SOCIAL MEDIA AND TESTING ROOM
def get_gemini_response(prompt):
    """
    Sends a prompt to the Google Gemini API and returns the text response.
    This is a simple text-in, text-out function.
    """
    try:
        # Configure the API key from environment variables
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY not found in environment variables.")
            return "Sorry, there's a configuration issue with the AI service."
            
        genai.configure(api_key=api_key)

        # Create a GenerativeModel instance
        # We use gemini-1.5-flash as it's fast and effective for this task
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate content
        response = model.generate_content(prompt)

        # Return the text part of the response
        return response.text

    except Exception as e:
        # Print the error for debugging on the server
        print(f"An error occurred in get_gemini_response: {e}")
        # Return a generic error message to the user
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."
    






# This is the complete and correct version for your Gemini-powered assistant

# def get_assistant_response(user_object, history, new_message):
#     try:
#         api_key = os.environ.get("GOOGLE_API_KEY")
#         if not api_key:
#             return "Sorry, there's a configuration issue with the AI service."
#         genai.configure(api_key=api_key)

#         # --- Using the SUPERIOR two-tool design ---
#         def get_my_business_profile() -> str:
#             """Fetches the complete business profile for the currently logged-in user."""
#             return get_entire_business_profile(user_id=user_object.id)

#         def update_my_business_profile(
#             business_name: str = None, owner_name: str = None, contact_number: str = None,
#             business_email: str = None, address: str = None, operating_hours: str = None,
#             social_media_links: str = None, usp: str = None, target_market: str = None,
#             audience_profile: str = None, product_categories: str = None, inventory_update_frequency: str = None,
#             top_selling_products: str = None, combo_packs: str = None, return_policy: str = None,
#             faqs: str = None
#         ) -> dict:
#             """Updates one or more fields in the user's business profile."""
#             updates = {k: v for k, v in locals().items() if v is not None}
#             return update_business_profile(user_id=user_object.id, **updates)

#         generation_config = {"temperature": 0}
#         model = genai.GenerativeModel(
#             model_name='gemini-1.5-flash', # Using the more reliable Pro model
#             tools=[get_my_business_profile, update_my_business_profile],
#             system_instruction="You are a helpful and intelligent business assistant... When a user asks a question, you MUST use the `get_my_business_profile` tool. When they ask to update, you MUST use the `update_my_business_profile` tool."
#         )
        
#         chat_session = model.start_chat(history=history)
#         response = chat_session.send_message(new_message)
        
#         # --- Using the CORRECT tool-handling logic ---
#         response_part = response.candidates[0].content.parts[0]
#         if response_part.function_call and response_part.function_call.name:
#             function_call = response_part.function_call
#             tool_name = function_call.name
            
#             tool_to_call = {
#                 "get_my_business_profile": get_my_business_profile,
#                 "update_my_business_profile": update_my_business_profile,
#             }.get(tool_name)

#             if not tool_to_call:
#                  return f"Error: The AI tried to use an unknown tool: {tool_name}"

#             tool_args = {key: value for key, value in function_call.args.items()}
#             tool_response_content = tool_to_call(**tool_args)
            
#             tool_response_part = {"function_response": {"name": tool_name,"response": {"content": tool_response_content}}}
#             second_response = chat_session.send_message(content=tool_response_part)
            
#             return second_response.text
#         else:
#             return response.text

#     except Exception as e:
#         print(f"An error occurred in get_assistant_response: {e}")
#         traceback.print_exc()
#         return "I'm sorry, an error occurred while processing your request. Please check the system logs."




def get_assistant_response(user_object, history, new_message):
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Sorry, there's a configuration issue with the AI service."
        genai.configure(api_key=api_key)

        # --- Defining the NEW, SIMPLER wrapper tools ---
        def get_field(field_name: str) -> str:
            """Use this tool to get the value of a specific field from the user's business profile."""
            return get_business_profile_field(user_id=user_object.id, field_name=field_name)

        def update_field(field_name: str, new_value: str) -> str:
            """Use this tool to update a specific field in the user's business profile with a new value."""
            return update_business_profile_field(user_id=user_object.id, field_name=field_name, new_value=new_value)

        generation_config = {"temperature": 0}
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', # Using the Flash model
            tools=[get_field, update_field], # Giving the AI the new, simple tools
            # --- A NEW, SIMPLER SYSTEM PROMPT ---
            system_instruction=(
                "You are a helpful business assistant. "
                "To answer questions about the user's profile, use the `get_field` tool. "
                "To change information, use the `update_field` tool. "
                "You must map natural language to the correct `field_name`. For example, 'brand name' or 'company name' should be mapped to 'business_name'. 'Phone number' should be mapped to 'contact_number'. "
                "The available field names are: business_name, description, owner_name, contact_number, business_email, address, operating_hours, social_media_links, usp, target_market, audience_profile, product_categories, inventory_update_frequency, top_selling_products, combo_packs, return_policy, faqs."
            )
        )
        
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(new_message)
        
        # This full tool-handling logic is still correct.
        response_part = response.candidates[0].content.parts[0]
        if response_part.function_call and response_part.function_call.name:
            function_call = response_part.function_call
            tool_name = function_call.name
            
            tool_to_call = {"get_field": get_field, "update_field": update_field}.get(tool_name)

            if not tool_to_call:
                 return f"Error: The AI tried to use an unknown tool: {tool_name}"

            tool_args = {key: value for key, value in function_call.args.items()}
            tool_response_content = tool_to_call(**tool_args)
            
            tool_response_part = {"function_response": {"name": tool_name,"response": {"content": tool_response_content}}}
            second_response = chat_session.send_message(content=tool_response_part)
            
            return second_response.text
        else:
            return response.text

    except Exception as e:
        print(f"An error occurred in get_assistant_response: {e}")
        traceback.print_exc()
        return "I'm sorry, an error occurred while processing your request. Please check the system logs."