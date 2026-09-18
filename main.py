import speech_recognition as sr

from memory import remember, recall, load_memory, save_memory
from ai import ask_ai
from voice import speak


# Create the speech recognizer
recognizer = sr.Recognizer()


# Listen to the user's voice and convert it to text
def listen():
    with sr.Microphone() as source:
        print("SWITCH is listening...")
        audio = recognizer.listen(source)

    try:
        # Convert recorded voice into text
        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        # Don't say anything if speech wasn't understood
        return None

    except sr.RequestError as error:
        print("Speech recognition service error:", error)
        return None


# Decide what SWITCH should do with the user's command
def process_command(text):

    text = text.lower()


    # ---------------- MEMORY COMMANDS ----------------

    # Forget something
    if text.startswith("forget my "):
        key = text.replace("forget my ", "").strip()

        memory = load_memory()

        if key in memory:
            del memory[key]
            save_memory(memory)

            response = f"I forgot your {key}."
        else:
            response = f"I don't remember your {key}."


    # Remember user's name
    elif "my name is" in text:
        name = text.replace("my name is", "").strip()

        remember("name", name)

        response = f"I'll remember that your name is {name}."


    # Remember something like:
    # "my favourite bike is CB1100"
    elif text.startswith("my ") and " is " in text:
        information = text[3:]

        key, value = information.split(" is ", 1)

        remember(key.strip(), value.strip())

        response = f"I'll remember that your {key.strip()} is {value.strip()}."


    # Remember something like:
    # "remember that my favourite colour is blue"
    elif "remember that" in text:
        information = text.replace("remember that", "").strip()

        if " is " in information:
            key, value = information.split(" is ", 1)

            remember(key.strip(), value.strip())

            response = f"I'll remember that your {key.strip()} is {value.strip()}."
        else:
            response = "Tell me what you want me to remember."


    # ---------------- RECALL COMMANDS ----------------

    # Recall name
    elif "what is my name" in text or "what's my name" in text:
        name = recall("name")

        if name:
            response = f"Your name is {name}."
        else:
            response = "I don't know your name yet."


    # Recall other memories
    elif "what is my" in text:
        key = text.replace("what is my", "").strip()

        value = recall(key)

        if value:
            response = f"Your {key} is {value}."
        else:
            response = f"I don't remember your {key}."


    # ---------------- AI COMMANDS ----------------

    else:
        # Load long-term memory
        memory = load_memory()

        # Ask the AI
        response = ask_ai(text, memory)


    # Show SWITCH's response
    print("SWITCH:", response)

    # Speak SWITCH's response
    speak(response)


# ---------------- MAIN LOOP ----------------

while True:

    # Listen to the user
    text = listen()

    # If nothing understandable was heard,
    # listen again silently
    if not text:
        continue


    # Shutdown command
    if text.lower() == "exit":
        speak("Goodbye.")
        print("SWITCH is shutting down.")
        break


    # Process the command
    process_command(text)