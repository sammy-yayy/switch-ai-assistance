import pyttsx3


def speak(text):
    # Create a fresh TTS engine every time
    engine = pyttsx3.init()

    # Get installed Windows voices
    voices = engine.getProperty("voices")

    # Use Microsoft Zira (female)
    engine.setProperty("voice", voices[1].id)

    # Voice settings
    engine.setProperty("rate", 145)
    engine.setProperty("volume", 1.0)

    # Speak
    engine.say(text)
    engine.runAndWait()

    # Properly stop the engine
    engine.stop()