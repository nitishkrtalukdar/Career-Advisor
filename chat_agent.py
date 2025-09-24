# In chat_agent.py, replace everything with this code

import google.generativeai as genai
import os

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def call_chat_agent(messages: list, system_prompt: str):
    model = genai.GenerativeModel('gemini-1.5-pro-latest',
                                  system_instruction=system_prompt)
    
    # --- THIS IS THE NEW, CRITICAL FIX ---
    # Convert the message history to the format Gemini's API requires.
    # The API expects a 'parts' key with a list containing the text.
    formatted_messages = []
    for msg in messages:
        # The role must be "user" or "model"
        if msg.get("role") in ["user", "model"]:
            formatted_messages.append({
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            })

    response = model.generate_content(
        formatted_messages, # Send the newly formatted list
        stream=True,
    )
    return response