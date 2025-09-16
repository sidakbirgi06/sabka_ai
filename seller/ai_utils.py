import os
import google.generativeai as genai 
import traceback
from .business_tools import get_entire_business_profile, update_business_profile
import json
from huggingface_hub import InferenceClient
import requests



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
# def get_assistant_response(user_object, history, new_message):
#     """
#     Handles conversations using a stateful ChatSession and a single, robust master tool.
#     """
#     try:
#         api_key = os.environ.get("GOOGLE_API_KEY")
#         if not api_key:
#             return "Sorry, there's a configuration issue with the AI service."
#         genai.configure(api_key=api_key)

#         # The AI will only see this one, simple-to-understand tool
#         def master_tool_wrapper(
#             action: str,  # AI will provide 'READ' or 'WRITE'
#             **kwargs
#         ) -> str:
#             """
#             The single tool to read or update the user's business profile.
#             To get information, set action to 'READ'.
#             To change information, set action to 'WRITE' and provide the fields to update as arguments.
#             """
#             # We convert the string action from the AI to our safe Enum
#             action_enum = ProfileAction[action]
#             return manage_business_profile(user_id=user_object.id, action=action_enum, **kwargs)


#         generation_config = {"temperature": 0.2} # Setting a low temp for reliability

#         model = genai.GenerativeModel(
#             model_name='gemini-1.5-flash',
#             tools=[master_tool_wrapper],
#             # --- A NEW, SUPERIOR SYSTEM PROMPT ---
#             system_instruction=(
#                 "You are Karya AI, an intelligent business assistant. Your purpose is to help users manage their business profile using your one and only tool: `master_tool_wrapper`."
#                 "\n\n"
#                 "**YOUR CORE DIRECTIVES:**"
#                 "\n1. **TO ANSWER QUESTIONS:** When the user asks ANY question about their profile (e.g., 'what is my name?', 'what is my usp?', 'tell me my address'), you MUST call `master_tool_wrapper` with the `action` parameter set to `'READ'`."
#                 "\n2. **TO MAKE CHANGES:** When the user asks you to change, update, or add ANY information to their profile, you MUST call `master_tool_wrapper` with the `action` parameter set to `'WRITE'` and provide the specific fields to change as arguments (e.g., `business_name='New Name'`)."
#                 "\n\n"
#                 "**VALID FIELDS:**"
#                 "\nThe valid fields you can READ or WRITE are:"
#                 "\n- business_name"
#                 "\n- description"
#                 "\n- owner_name"
#                 "\n- contact_number"
#                 "\n- business_email"
#                 "\n- address"
#                 "\n- operating_hours"
#                 "\n- social_media_links"
#                 "\n- usp"
#                 "\n- target_market"
#                 "\n- audience_profile"
#                 "\n- product_categories"
#                 "\n- inventory_update_frequency"
#                 "\n- top_selling_products"
#                 "\n- combo_packs"
#                 "\n- accepts_cod"
#                 "\n- accepts_upi"
#                 "\n- accepts_card"
#                 "\n- delivery_methods"
#                 "\n- return_policy"
#                 "\n- faqs"
#                 "\nAlways use these exact snake_case names when calling the tool. Do not invent new field names."
#                 "\n\n"
#                 "**COMMUNICATION RULES:**"
#                 "\n- Communicate concisely and professionally."
#                 "\n- After a successful WRITE action, confirm the change to the user."
#                 "\n- NEVER mention your tool names or the `action` parameter. Interact naturally."
#                 "\n- Do not make up information. If the data is not in the profile after a READ action, say it is not set."
#             ),
#             generation_config=generation_config
#         )
        
#         # This ChatSession logic is correct.
#         chat_session = model.start_chat(history=history)
#         response = chat_session.send_message(new_message)
        
#         response_part = response.candidates[0].content.parts[0]
#         if response_part.function_call and response_part.function_call.name:
#             function_call = response_part.function_call
#             tool_name = function_call.name # Will always be 'master_tool_wrapper'
            
#             tool_to_call = master_tool_wrapper # We can call it directly

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







# FOR BUSINESS ASSISTANT (Powered by Hugging Face)
# ==============================================================================

# --- The direct URL to the Hugging Face API endpoint for our chosen model ---
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# The master prompt that teaches the model how to behave and use our tools.
SYSTEM_PROMPT = """You are Karya AI, an intelligent and helpful business assistant. Your goal is to help the user manage their business profile. You have two tools available:

1. `get_entire_business_profile()`: Use this tool when the user asks a question about their business (e.g., "what is my usp?", "tell me my hours"). This tool takes no parameters.

2. `update_business_profile(parameters)`: Use this tool when the user asks to change, update, or add information. This tool requires parameters.

**CRITICAL RULE:** When you decide to use a tool, you MUST respond ONLY with a JSON object in the following format, and nothing else.

{
  "tool_to_call": "<name_of_the_tool_to_call>",
  "parameters": {
    "parameter_name": "parameter_value"
  }
}

If you are not calling a tool, just respond naturally to the user.
"""

def hf_api_call(prompt):
    """A dedicated function for making a direct, manual call to the HF API."""
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 1024, "temperature": 0.1, "return_full_text": False}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status() # This will raise an error if the request fails
    return response.json()[0]['generated_text']


def get_assistant_response(user_object, history, new_message):
    """
    Handles conversations by making direct HTTP requests to the Hugging Face API.
    """
    try:
        history_string = ""
        for item in history:
            role = "User" if item['role'] == 'user' else "AI"
            content = item['parts'][0]['text']
            history_string += f"{role}: {content}\n"
        
        final_prompt = f"{SYSTEM_PROMPT}\n\n--- Conversation History ---\n{history_string}User: {new_message}\nAI:"

        # 1. First call to the model to see if it wants to use a tool
        response_text = hf_api_call(final_prompt)

        try:
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            tool_call_data = json.loads(cleaned_response)

            if "tool_to_call" in tool_call_data and "parameters" in tool_call_data:
                tool_name = tool_call_data["tool_to_call"]
                parameters = tool_call_data["parameters"]
                
                tool_result = ""
                if tool_name == "get_entire_business_profile":
                    tool_result = get_entire_business_profile(user_id=user_object.id)
                elif tool_name == "update_business_profile":
                    tool_result = update_business_profile(user_id=user_object.id, **parameters)
                else:
                    return "I tried to use a tool that doesn't exist."

                # 2. Second call to the model to summarize the tool's result
                summarization_prompt = f"--- Conversation History ---\n{history_string}User: {new_message}\nAI: [Executed tool '{tool_name}' and got this result: {tool_result}]\nBased on this result, formulate a natural language response to the user:"
                final_reply = hf_api_call(summarization_prompt)
                return final_reply.strip()
        
        except (json.JSONDecodeError, TypeError, KeyError):
            return response_text.strip()

    except Exception as e:
        print(f"An error occurred in get_assistant_response: {e}")
        traceback.print_exc()
        return "I'm sorry, an error occurred while processing your request. Please check the system logs."