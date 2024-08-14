import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory
from groq import AsyncGroq
import asyncio
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize the AsyncGroq client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))


@app.route('/')
def home():
    app.logger.info("Rendering home page")
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    app.logger.info(f"Serving static file: {filename}")
    return send_from_directory(app.static_folder, filename)


@app.route('/chat', methods=['POST'])
def chat():
    try:
        app.logger.info("Received chat request")
        user_message = request.json['message']
        chat_history = request.json['history']

        app.logger.debug(f"User message: {user_message}")
        app.logger.debug(f"Chat history: {chat_history}")

        # Prepare messages for the API call
        messages = []
        for chat in chat_history:
            if isinstance(chat, dict):
                messages.append({"role": "user", "content": chat.get('user', '')})
                messages.append({"role": "assistant", "content": chat.get('bot', '')})
            else:
                app.logger.warning(f"Unexpected chat history format: {chat}")
        messages.append({"role": "user", "content": user_message})

        # Use asyncio to run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(get_llama_response(messages))

        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


async def get_llama_response(messages):
    try:
        app.logger.info("Sending request to Groq API")
        response_content = ""
        stream = await client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                response_content += content
        app.logger.info("Received response from Groq API")
        return response_content
    except Exception as e:
        app.logger.error(f"An error occurred in get_llama_response: {str(e)}")
        app.logger.error(traceback.format_exc())
        raise


if __name__ == '__main__':
    app.logger.info(f"Static folder is located at: {app.static_folder}")
    app.logger.info(f"Template folder is located at: {app.template_folder}")
    app.run(debug=True)