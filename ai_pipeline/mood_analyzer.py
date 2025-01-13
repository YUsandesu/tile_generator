from deepface import DeepFace

def analyze_mood(photo_path):
    analysis = DeepFace.analyze(img_path=photo_path, actions=['emotion'])
    print("[Progress] Obtain DeepFace Results")
    mood_result = analysis[0]['emotion']
    moods, values = [], []
    for mood, value in mood_result.items():
        moods.append(mood)
        values.append(value)
    print("[Progress] Sorting For The Mood")
    return moods[values.index(max(values))]


if __name__ == "__main__":
    mood = analyze_mood('captured.jpg')
    print(mood)