from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
import os
import time
import re
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-8b")

app = Flask(__name__, static_folder='../static', template_folder='../templates')


from google.auth.exceptions import GoogleAuthError

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
        except GoogleAuthError as e:
            print(f"Authentication error: {e}. Please check your API key.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
    return "Failed to get a response after multiple attempts."


# Preprocess the content to clean the response
def preprocess_content(content):
    content = re.sub(r'^[#*].*', '', content)  # Remove lines with markdown or special chars
    content = re.sub(r'^\s*(This (is|was).*)|(\(.*\))|(\*|#).*$', '', content)  # Remove unwanted lines
    content = re.sub(r'\*\*', '', content)  # Remove bold markdown (**)
    content = re.sub(r'\*', '', content)    # Remove other markdown characters (*)
    content = re.sub(r'#', '', content)    # Remove markdown header symbols (#)
    content = re.sub(r'\n+', '\n', content).strip()  # Remove extra newlines
    return content


# Pre-work prompt for Gemini: to act as a lawyer and provide specific answers
def generate_lawyer_prompt(user_query):
    prompt = f"""
    You are a lawyer. Please provide a direct and specific answer to the following question without adding any extra information:
    Question: {user_query}
    """
    return prompt


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/legal")
def legal():
    return render_template("legal.html")

@app.route("/finance")
def finance():
    return render_template("finance.html")

@app.route("/ask", methods=["POST"])
def ask_question():
    user_query = request.json.get('question')  # Get the user question from the request

    if user_query:
        # Generate the pre-prompt to instruct Gemini on how to behave
        lawyer_prompt = generate_lawyer_prompt(user_query)
        
        # Get the response from Gemini
        response_text = get_gemini_response(gemini_model, lawyer_prompt)
        
        # Clean up the response before sending it to the client
        processed_response = preprocess_content(response_text)
        
        return jsonify({'answer': processed_response})
    
    return jsonify({'answer': "Sorry, I couldn't understand your question."})
@app.route("/talk_lawyer", methods=["POST"])
def talk_lawyer():
    user_query = request.json.get('question')

    if user_query:
        lawyer_prompt = generate_lawyer_prompt(user_query)  # Pre-prompt for lawyer style answer
        response_text = get_gemini_response(gemini_model, lawyer_prompt)  # Call Gemini
        processed_response = preprocess_content(response_text)  # Clean response
        return jsonify({'answer': processed_response})
    
    return jsonify({'answer': "Sorry, I couldn't understand your question."})

if __name__ == "__main__":
    app.run(debug=True)
