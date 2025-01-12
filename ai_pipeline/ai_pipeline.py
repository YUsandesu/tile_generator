from google import genai
import os
from captured_photo import capture_photo
from mood_analyzer import analyze_mood
from article_generation import generate_narrative
from music_generation import save_generated_music

if __name__ == "__main__":
    llm_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    print("[Progress] Create A Google AI Client")
    capture_photo()
    mood = analyze_mood('captured.jpg')
    narrative = generate_narrative(llm_client, "captured.jpg", mood)
    save_generated_music(narrative, llm_client)
    