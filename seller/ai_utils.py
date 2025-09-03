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
def get_assistant_response(user_message, user_object):
    """
    Handles conversations for the Business Assistant.
    It's configured with tools to interact with the database.
    """
    try:
        # Configure the API key from environment variables
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY not found in environment variables.")
            return "Sorry, there's a configuration issue with the AI service."

        genai.configure(api_key=api_key)

        # IMPORTANT: Configure the model with our specific tools and system prompt
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

        # Start a chat session and send the user's message
        chat_session = model.start_chat()
        response = chat_session.send_message(user_message)

        # Manual Function Calling: Check if the model wants to use a tool
        for function_call in response.function_calls:
            # Get the name of the tool the AI wants to use
            tool_name = function_call.name
            
            # Find the actual Python function to call
            tool_to_call = {
                "get_entire_business_profile": get_entire_business_profile,
                "update_business_profile": update_business_profile,
            }[tool_name]
            
            # Get the arguments from the AI
            tool_args = function_call.args
            
            # CRITICAL: Inject the logged-in user object into the arguments
            tool_args["user"] = user_object
            
            # Call the tool with the combined arguments
            tool_response = tool_to_call(**tool_args)
            
            # Send the tool's output back to the model
            response = chat_session.send_message(
                genai.Part(function_response=genai.FunctionResponse(
                    name=tool_name,
                    response=tool_response,
                ))
            )

        return response.text

    except Exception as e:
        print(f"An error occurred in get_assistant_response: {e}")
        return "I'm sorry, an error occurred while processing your request. Please check the system logs."