import os
import google.generativeai as genai
from .business_tools import get_entire_business_profile, update_business_profile
import traceback



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
    


# FOR BUSINESS ASSITANT 
# FOR BUSINESS ASSISTANT
# --- CHANGE 1: We REMOVE the 'user_message' parameter ---
def get_assistant_response(user_object, history):
    """
    Handles conversations for the Business Assistant using user-aware tools.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Sorry, there's a configuration issue with the AI service."

        genai.configure(api_key=api_key)

        # --- MAJOR CHANGE 1: Create User-Aware "Wrapper" Tools ---
        # These functions "hide" the user_id from the AI. The AI will see simple
        # tools like get_my_business_profile() with no arguments needed.

        def get_my_business_profile() -> str:
            """Fetches the business profile for the currently logged-in user."""
            return get_entire_business_profile(user_id=user_object.id)

        def update_my_business_profile(**updates: dict) -> dict:
            """Updates the business profile for the currently logged-in user."""
            return update_business_profile(user_id=user_object.id, **updates)


        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            # --- MAJOR CHANGE 2: Give the AI the NEW, simpler tools ---
            tools=[get_my_business_profile, update_my_business_profile],
            system_instruction=(
                "You are a helpful and intelligent business assistant for the 'Karya AI' platform. "
                "Your primary goal is to help the user manage their business profile by answering their questions and updating their information using the provided tools. "
                # --- MAJOR CHANGE 3: REMOVE the confusing rule about user_id ---
                # The AI no longer needs this rule because it never sees 'user_id' anymore.
                "\n\n"
                "**Communication Rules:**\n"
                "- Communicate in a friendly, professional, and concise manner.\n"
                "- NEVER mention that you are an AI or a language model.\n"
                "- CRITICALLY, NEVER reveal the names of the internal tools or functions you are using. Frame all your responses naturally.\n"
                "\n\n"
                "**Tool Usage Rules:**\n"
                "- When the user asks to update information, be flexible. Map natural language to the correct database field names. For example, if 'owners name' is said, map it to the 'owner_name' field.\n"
                "- Here are the available fields for the update tool: 'business_name', 'owner_name', 'contact_number', 'business_email', 'address', 'operating_hours', 'social_media_links', 'usp', 'target_market', 'audience_profile', 'product_categories', 'inventory_update_frequency', 'top_selling_products', 'combo_packs', 'return_policy', 'faqs'."
            )
        )
        
        response = model.generate_content(history)
        response_part = response.candidates[0].content.parts[0]

        if response_part.function_call and response_part.function_call.name:
            function_call = response_part.function_call
            tool_name = function_call.name
            
            # --- MAJOR CHANGE 4: The system now calls the NEW tool names ---
            tool_to_call = {
                "get_my_business_profile": get_my_business_profile,
                "update_my_business_profile": update_my_business_profile,
            }.get(tool_name)

            if not tool_to_call:
                 return f"Error: The AI tried to use an unknown tool: {tool_name}"

            tool_args = {key: value for key, value in function_call.args.items()}
            
            # We no longer need to pass user_id here, as it's already baked into the functions.
            tool_response_content = tool_to_call(**tool_args)
            
            second_response = model.generate_content(
                [
                    *history,
                    genai.Part(function_response=genai.FunctionResponse(
                        name=tool_name,
                        response={"content": tool_response_content},
                    ))
                ]
            )
            return second_response.text
        else:
            return response.text

    except Exception as e:
        print(f"An error occurred in get_assistant_response: {e}")
        traceback.print_exc()
        return "I'm sorry, an error occurred while processing your request. Please check the system logs."