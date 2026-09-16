import speech_recognition as sr

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


def process_command(text):      #This is where SWITCH will decide what to do with what you said.
    print("You said:", text)


# Keep SWITCH running until the user says "exit"
while True:
    text = listen()

    if text and text.lower() == "peace out":
        print("SWITCH is shutting down.")
        break

    if text:
        process_command(text)