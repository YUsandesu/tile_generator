from google import genai
import PIL
import os

def generate_narrative(llm_client, image_path, mood, model_name='gemini-2.0-flash-exp'):
    """
    Generates a narrative description of an image based on a mood using the Gemini API.

    Args:
        image_path (str): Path to the image file.
        mood (str): The desired mood or emotion for the description.
        model_name (str): Which Google model you want to use to generate a description, default to 'gemini-pro-vision'.

    Returns:
        str: The generated narrative text.
    """

    try:
        image = PIL.Image.open(image_path)
    except FileNotFoundError:
        return "[Error] Image not found..."
    except Exception as e:
        return f"[Error] Could not open image: {e}"

    prompt = f"""
        Generate a narrative description of this image, capturing a mood that is {mood}.
        Imagine a whole story. Focus on the feeling it conveys.
    """
    print(f"[Progress] Prompt For The Narrative Generation\n{prompt}")

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    try:
        response = llm_client.models.generate_content(
            model=model_name,
            contents=[prompt, image],
            config=genai.types.GenerateContentConfig(**generation_config),
        )
        print("[Progress] Obtain Generated Text Result From Google")
        return response.text
    except Exception as e:
        return f"[Error] Failed to generate: {e}"


if __name__ == "__main__":
    image_file_path = "captured_photo.jpg"
    llm_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    mood = "joyful and serene"
    narrative = generate_narrative(llm_client, image_file_path, mood)
    print(f"Mood: {mood}\nNarrative:\n{narrative}\n")
    mood = "melancholy and reflective"
    narrative = generate_narrative(llm_client, image_file_path, mood)
    print(f"Mood: {mood}\nNarrative:\n{narrative}\n")