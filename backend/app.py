from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
import os
import time
import re
import requests
from dotenv import load_dotenv

app = Flask(__name__, static_folder='../static', template_folder='../templates')
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")


def get_gemini_response(model, message):
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            chat = model.start_chat()
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


# Preprocess the content
def preprocess_content(content):
    content = re.sub(r'^[#*].*', '', content)  # Remove lines with markdown or special chars
    content = re.sub(r'^\s*(This (is|was).*)|(\(.*\))|(\*|#).*$', '', content)  # Remove unwanted lines
    content = re.sub(r'\*\*', '', content)  # Remove bold markdown (**)
    content = re.sub(r'\*', '', content)    # Remove other markdown characters (*)
    content = re.sub(r'#', '', content)    # Remove markdown header symbols (#)
    content = re.sub(r'\n+', '\n', content).strip()  # Remove extra newlines
    return content


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask_question():
    user_query = request.json.get('question')  # Change to handle JSON payload
    
    if user_query:
        response_text = get_gemini_response(gemini_model, user_query)
        processed_response = preprocess_content(response_text)  # Clean up the response
        return jsonify({'answer': processed_response})
    
    return jsonify({'answer': "Sorry, I couldn't understand your question."})



if __name__ == "__main__":
    app.run(debug=True)
