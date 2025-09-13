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
def get_assistant_response(user_object, history):
    """
    Handles conversations for the Business Assistant using user-aware tools.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Sorry, there's a configuration issue with the AI service."

        genai.configure(api_key=api_key)

        # --- THE FIX IS HERE: We are making the tool descriptions much clearer ---

        def get_my_business_profile() -> str:
            """
            Fetches and returns all information from the user's business profile.
            This includes details like business name, address, products, and FAQs.
            """
            return get_entire_business_profile(user_id=user_object.id)

        def update_my_business_profile(**updates: dict) -> dict:
            """
            Updates one or more fields in the user's business profile.
            Use this to change details like the business_name, contact_number, address, etc.
            The 'updates' argument must be a dictionary where keys are the field names
            (e.g., 'business_name') and values are the new values.
            """
            return update_business_profile(user_id=user_object.id, **updates)

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[get_my_business_profile, update_my_business_profile],
            system_instruction=(
                # Your system instruction is good and remains the same.
                "You are a helpful and intelligent business assistant for the 'Karya AI' platform..."
            )
        )
        
        # (The rest of the function is now correct and remains unchanged)
        response = model.generate_content(history)
        response_part = response.candidates[0].content.parts[0]

        if response_part.function_call and response_part.function_call.name:
            # ... (all the tool-calling logic is correct)
            function_call = response_part.function_call
            tool_name = function_call.name
            
            tool_to_call = {
                "get_my_business_profile": get_my_business_profile,
                "update_my_business_profile": update_my_business_profile,
            }.get(tool_name)

            if not tool_to_call:
                 return f"Error: The AI tried to use an unknown tool: {tool_name}"

            tool_args = {key: value for key, value in function_call.args.items()}
            tool_response_content = tool_to_call(**tool_args)
            
            tool_response_part = {
                "function_response": {
                    "name": tool_name,
                    "response": {"content": tool_response_content},
                }
            }

            second_response = model.generate_content([*history, tool_response_part])
            return second_response.text
        else:
            return response.text

    except Exception as e:
        print(f"An error occurred in get_assistant_response: {e}")
        traceback.print_exc()
        return "I'm sorry, an error occurred while processing your request. Please check the system logs."