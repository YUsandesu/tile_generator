from midi_convertor import parse_text_music
import time
import os
from google import genai

def generate_music_from_text(text_input, llm_client):
    """
    Generates music from text input using the LLM.
    """
    print("[Progress] Generating Music Using Text...")
    prompt = f"""
        Generate a musical phrase directly, reflecting the text's content and emotion, using this strict format only:

        -  `[Chord]` for chord changes (e.g., [Am], [Cmaj7], [G], [D]).
        -  `<>` for dynamics, with `f` for forte (e.g., <f>).
        -  `Note-duration` for notes and durations (e.g., A3-1/2, G4-1, C5-1/4). Durations are in beats.
        -  `$tempo` for tempo changes in BPM (e.g., $120).
        -  `|` to separate phrases.

        Do not include any introductory text, explanations, or conversational phrases. Output *only* the music string.

        Text: {text_input}
    """
    print(f"[Progress] Prompt For The Music Generation\n{prompt}")
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    response = llm_client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config=genai.types.GenerateContentConfig(**generation_config),
    )
    music_string = response.text.strip()
    if music_string.startswith("Okay, here's a musical phrase designed to reflect "):
        music_string = music_string.replace("Okay, here's a musical phrase designed to reflect ", "").strip()
    if music_string.startswith("Okay, here's the musical phrase as requested:"):
         music_string = music_string.replace("Okay, here's the musical phrase as requested:", "").strip()
    print("[Progress] Obtain Generated Music Note String From Google")
    return music_string

def save_generated_music(text_input, llm_client):
    start_time = time.time()
    music_string = generate_music_from_text(text_input, llm_client)
    try:
        my_stream = parse_text_music(music_string)
        print("[Progress] Obtained The Generated Music. Saving It...")
        my_stream.write('midi', fp='music.mid')
    except Exception as e:
        print(f"[Error] Parsing generated music string: {e}. Music output: {music_string}")
    print(f"[Progress] Music Section Done in {time.time() - start_time: .2f} seconds")
     
      
if __name__ == "__main__":
    llm_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    save_generated_music("A bright sunny day.", llm_client)
    # save_generated_music("The dark forest was scary", llm_client)