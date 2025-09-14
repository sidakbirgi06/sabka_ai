import os
import google.generativeai as genai 
import traceback
from .business_tools import manage_business_profile, ProfileAction



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
def get_assistant_response(user_object, history, new_message):
    """
    Handles conversations using a stateful ChatSession and a single, robust master tool.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "Sorry, there's a configuration issue with the AI service."
        genai.configure(api_key=api_key)

        # The AI will only see this one, simple-to-understand tool
        def master_tool_wrapper(
            action: str,  # AI will provide 'READ' or 'WRITE'
            **kwargs
        ) -> str:
            """
            The single tool to read or update the user's business profile.
            To get information, set action to 'READ'.
            To change information, set action to 'WRITE' and provide the fields to update as arguments.
            """
            # We convert the string action from the AI to our safe Enum
            action_enum = ProfileAction[action]
            return manage_business_profile(user_id=user_object.id, action=action_enum, **kwargs)


        generation_config = {"temperature": 0.2} # Setting a low temp for reliability

        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[master_tool_wrapper],
            # --- A NEW, SUPERIOR SYSTEM PROMPT ---
            system_instruction=(
                "You are Karya AI, an intelligent business assistant. Your purpose is to help users manage their business profile using your one and only tool: `master_tool_wrapper`."
                "\n\n"
                "**YOUR CORE DIRECTIVES:**"
                "\n1. **TO ANSWER QUESTIONS:** When the user asks ANY question about their profile (e.g., 'what is my name?', 'what is my usp?', 'tell me my address'), you MUST call `master_tool_wrapper` with the `action` parameter set to `'READ'`."
                "\n2. **TO MAKE CHANGES:** When the user asks you to change, update, or add ANY information to their profile, you MUST call `master_tool_wrapper` with the `action` parameter set to `'WRITE'` and provide the specific fields to change as arguments (e.g., `business_name='New Name'`)."
                "\n\n"
                "**VALID FIELDS:**"
                "\nThe valid fields you can READ or WRITE are:"
                "\n- business_name"
                "\n- description"
                "\n- owner_name"
                "\n- contact_number"
                "\n- business_email"
                "\n- address"
                "\n- operating_hours"
                "\n- social_media_links"
                "\n- usp"
                "\n- target_market"
                "\n- audience_profile"
                "\n- product_categories"
                "\n- inventory_update_frequency"
                "\n- top_selling_products"
                "\n- combo_packs"
                "\n- accepts_cod"
                "\n- accepts_upi"
                "\n- accepts_card"
                "\n- delivery_methods"
                "\n- return_policy"
                "\n- faqs"
                "\nAlways use these exact snake_case names when calling the tool. Do not invent new field names."
                "\n\n"
                "**COMMUNICATION RULES:**"
                "\n- Communicate concisely and professionally."
                "\n- After a successful WRITE action, confirm the change to the user."
                "\n- NEVER mention your tool names or the `action` parameter. Interact naturally."
                "\n- Do not make up information. If the data is not in the profile after a READ action, say it is not set."
            ),
            generation_config=generation_config
        )
        
        # This ChatSession logic is correct.
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(new_message)
        
        response_part = response.candidates[0].content.parts[0]
        if response_part.function_call and response_part.function_call.name:
            function_call = response_part.function_call
            tool_name = function_call.name # Will always be 'master_tool_wrapper'
            
            tool_to_call = master_tool_wrapper # We can call it directly

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