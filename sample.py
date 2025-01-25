import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
from google.api_core.exceptions import InternalServerError
import requests

# Load environment variables from .env
load_dotenv()

# Retrieve the API key from the environment
api_key = os.getenv("API_KEY")

# Ensure the API key is set
if not api_key:
    raise ValueError("API key not found. Please check your .env file.")

# Configure the Gemini API with the API key
genai.configure(api_key=api_key)

# Create the model object (adjust model name as per your setup)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")

def get_gemini_response(message):
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            chat = gemini_model.start_chat()
            response = chat.send_message(message)
            return response.text
        except InternalServerError as e:
            print(f"Attempt {attempt + 1} failed due to server error: {e}. Retrying...")
            time.sleep(2)
        except requests.exceptions.Timeout as e:
            print(f"Attempt {attempt + 1} failed due to timeout: {e}. Retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
    return "Failed to get a response after multiple attempts."

# Test the API key and send a sample message
message = "Hello, can you tell me about AI?"
response = get_gemini_response(message)
print(f"Response from Gemini: {response}")
