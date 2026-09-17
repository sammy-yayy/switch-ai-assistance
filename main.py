import speech_recognition as sr
from memory import remember, recall

recognizer = sr.Recognizer()


# Listen to the user's voice and convert it to text
def listen():
    with sr.Microphone() as source:
        print("SWITCH is listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        print("SWITCH couldn't understand you.")
        return None

    except sr.RequestError as error:
        print("Speech recognition service error:", error)
        return None


## This is where SWITCH will decide what to do with what you said. ##
def process_command(text):
    text = text.lower()

    if text.startswith("forget my "):
        key = text.replace("forget my ", "").strip()

        memory = load_memory()

        if key in memory:
            del memory[key]
            save_memory(memory)
            print(f"I forgot your {key}.")
        else:
            print(f"I don't remember your {key}.")

    elif "my name is" in text:
        name = text.replace("my name is", "").strip()
        remember("name", name)
        print(f"I'll remember that your name is {name}.")

    elif text.startswith("my ") and " is " in text:
        information = text[3:]
        key, value = information.split(" is ", 1)

        remember(key.strip(), value.strip())
        print(f"I'll remember that your {key.strip()} is {value.strip()}.")

    elif "remember that" in text:
        information = text.replace("remember that", "").strip()

        if " is " in information:
            key, value = information.split(" is ", 1)
            remember(key.strip(), value.strip())
            print(f"I'll remember that your {key.strip()} is {value.strip()}.")
        else:
            print("Tell me what you want me to remember.")

    elif "what is my name" in text or "what's my name" in text:
        name = recall("name")

        if name:
            print(f"Your name is {name}.")
        else:
            print("I don't know your name yet.")

    elif "what is my" in text:
        key = text.replace("what is my", "").strip()
        value = recall(key)

        if value:
            print(f"Your {key} is {value}.")
        else:
            print(f"I don't remember your {key}.")

    else:
        print("You said:", text)


# Keep SWITCH running until the user says "exit"
while True:
    text = listen()

    if text and text.lower() == "exit":
        print("SWITCH is shutting down.")
        break

    if text:
        process_command(text)