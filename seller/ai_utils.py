import os
import google.generativeai as genai
from .business_tools import get_entire_business_profile, update_business_profile



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
def get_assistant_response(history, user_object):
    """
    Handles conversations for the Business Assistant using conversation history.
    It's configured with tools to interact with the database.
    """
    # ... (the try block, api_key, genai.configure, and model setup are all the same) ...
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            #...
            return "..."
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            #... (model_name, tools, system_instruction are all the same) ...
        )

        chat_session = model.start_chat(history=history)
        last_user_message = history[-1]['parts'][0]['text']
        response = chat_session.send_message(last_user_message)
        
        if hasattr(response.candidates[0].content.parts[0], 'function_call'):
            function_call = response.candidates[0].content.parts[0].function_call
            tool_name = function_call.name
            tool_to_call = next((t for t in [get_entire_business_profile, update_business_profile] if t.__name__ == tool_name), None)

            if tool_to_call:
                tool_args = {key: value for key, value in function_call.args.items()}
                tool_args["user"] = user_object
                tool_response_content = tool_to_call(**tool_args)
                
                # --- KEY CHANGE ---
                # We now pass the dictionary from our tool directly as the response.
                # This is the correct format the API expects.
                response = chat_session.send_message(
                    genai.Part(function_response=genai.FunctionResponse(
                        name=tool_name,
                        response=tool_response_content, # Pass the dict directly
                    ))
                )

        return response.text

    except Exception as e:
        import traceback
        print(f"An error occurred in get_assistant_response:")
        traceback.print_exc()
        return "I'm sorry, an error occurred while processing your request. Please check the system logs."