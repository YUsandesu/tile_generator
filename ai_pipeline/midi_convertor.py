from music21 import note, stream, chord, tempo, pitch
from fractions import Fraction

def parse_text_music(text_music):
    """Parses music text and returns a music21 stream"""
    print("[Progress] Parsing Music Note...")
    s = stream.Stream()
    current_tempo = 120
    current_chord = None
    
    parts = text_music.split("|") # Split on the pipe symbol for phrase
    for part in parts:
        notes_and_chords = part.strip().split()
        dynamic = 70
        for item in notes_and_chords:
            if item.startswith('['):
                #Extract the chord and set the current chord
                chord_str = item[1:-1]
                try:
                  current_chord = chord.Chord(chord_str)
                except Exception as _:
                    root_note = pitch.Pitch(chord_str[0])
                    current_chord = chord.Chord([root_note, root_note.transpose('m3' if 'm' in chord_str else 'M3'), root_note.transpose('p5')])
                for n in current_chord.notes:
                    n.volume.velocity = dynamic
            elif item.startswith('<'):
                # Extract dynamics
                dynamic = item[1:-1]
                if dynamic == 'f':
                    dynamic = 127 # use any number between 0 and 127.
            elif item.startswith('$'):
                # Extract tempo
                current_tempo = int(item[1:])
                s.append(tempo.MetronomeMark(number=current_tempo))
            else: #must be a note
                note_parts = item.split('-') # parse the note info
                pitch_str = note_parts[0] # get pitch
                duration_str = note_parts[1] # get duration
                
                n = note.Note(pitch_str)
                n.duration.quarterLength = float(Fraction(duration_str))
                #Apply chord to the note if there is one
                if current_chord:
                    n.addLyric(str(current_chord))
                s.append(n)
    print("[Progress] Finished Parsing Music Note.")
    return s


if __name__ == "__main__":
    # Your musical text:
    text_music = """$70 [Am] <f> A3-1/2 E4-1/2 C4-1/2 A3-1 | [G] <f> D4-1/4 F#4-1/4 A4-1/4 G4-1/4  D5-1 | [C] C4-1 G3-1/2 E3-1/2 C4-2
    |$60 C4-1 G3-1/2 E3-1/2 C4-2"""
    my_stream = parse_text_music(text_music)
    my_stream.write('midi', fp='lonely_hero_enhanced.mid')