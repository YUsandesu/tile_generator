import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='high',
    config=types.GenerateContentConfig(**generation_config),
)

print(response.text)