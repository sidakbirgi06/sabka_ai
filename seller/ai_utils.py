# This is the new, full content for seller/ai_utils.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The specific Llama 3 model we want to use from Hugging Face
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_API_TOKEN = os.getenv('HF_API_TOKEN')

def get_ai_response(prompt):
    """
    Sends a prompt to the Hugging Face Inference API and returns the response.
    """
    if not HF_API_TOKEN:
        print("Error: Hugging Face API Token not found.")
        return "Sorry, the AI service is not configured correctly (missing API Token)."

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,  # Limit the length of the reply
            "return_full_text": False, # Only return the AI's generated part
            "temperature": 0.7, # A bit of creativity
        }
    }

    try:
        # We add a timeout to prevent the app from hanging indefinitely
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # This will raise an error if the response was bad (e.g., 4xx or 5xx)
        response.raise_for_status()  
        
        # The response is a list, so we get the first item's generated_text
        generated_text = response.json()[0]['generated_text']
        return generated_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error getting response from Hugging Face: {e}")
        # Check for model loading error (common on free tier)
        if e.response and "is currently loading" in e.response.text:
            return "My AI brain is warming up, please send your message again in a moment!"
        return "Sorry, I am having trouble connecting to my brain right now. Please try again in a moment."