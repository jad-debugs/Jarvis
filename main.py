from os import system
import speech_recognition as sr
from playsound import playsound
from gpt4all import GPT4All
from elevenlabs import play
from elevenlabs.client import ElevenLabs
import sys
import whisper
import warnings
import time
import os

# starts program
wake_word = 'jarvis'

# loading model gpt4falcon
model = GPT4All("/Users/jadisaac/Library/Application Support/nomic.ai/GPT4All/gpt4all-falcon-newbpe-q4_0.gguf", allow_download=False)

# speech recognition object
r = sr.Recognizer()

# whisper models, locally
tiny_path = os.path.expanduser('~/.cache/whisper/tiny.pt')
# base_path = os.path.expanduser('~/.cache/whisper/base.pt')

tiny_model = whisper.load_model(tiny_path)
# base_model = whisper.load_model(base_path)

listening_for_wake = True;

source = sr.Microphone()

warnings.filterwarnings("ignore", category=UserWarning, module='whisper.transcribe', lineno=114)

# client = ElevenLabs(api_key="bd488655ab5dcb76fc3aa3e450e56628")
client = ElevenLabs()
# if not macos, we r good
if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init()

# gpt result spoken in built in mac person sound
def speak(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGGHJKLZXCVBNM0123456789.,?!-_$:+/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        jarvis_response = client.generate(
            text=clean_text,
            voice="Adam",
        )
        play(jarvis_response)
    else:
        engine.say(text)
        engine.runAndWait()


def listen_for_wake(audio):
    global listening_for_wake 
    with open("wake_detect.wav", "wb") as f:
        f.write(audio.get_wav_data())
    result = tiny_model.transcribe('wake_detect.wav')
    text_input = result['text']
    if wake_word in text_input.lower().strip():
        print("Yes, Mr.Isaac")
        speak("Yes, Mr.Isaac")
        listening_for_wake = False

def prompt_gpt(audio):
    global listening_for_wake
    try:
        with open("prompt.wav", "wb") as f:
            f.write(audio.get_wav_data())
        result = tiny_model.transcribe('prompt.wav')
        prompt_text = result['text']
        if len(prompt_text.strip()) == 0:
            print("Guess you dont need help?")
            speak("Guess you dont need help?")
            listening_for_wake = True
        else:
            print("User : " + prompt_text)
            output = model.generate(prompt_text, max_tokens=200)
            print("GPT4ALL: ", output)
            speak(output)
            print("\nSay", wake_word, "to wake me back up, I'm gonna take a nap\n")
            listening_for_wake = True
    except Exception as e:
        print("Im going down, we might be hacked!", e)

def callback(recognizer, audio):
    global listening_for_wake
    if listening_for_wake == True:
        listen_for_wake(audio)
    else:
        prompt_gpt(audio)

def start_listening():
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2) 

    print("Say", wake_word)
    r.listen_in_background(source, callback)

    while True:
        time.sleep(1)

if __name__ == '__main__':
    start_listening()
