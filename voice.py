import pyttsx3


def speak(text):

    # Create a fresh TTS engine every time
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")

    # Microsoft Zira (female)
    engine.setProperty(
        "voice",
        voices[1].id
    )

    # Voice settings
    engine.setProperty(
        "rate",
        145
    )

    engine.setProperty(
        "volume",
        1.0
    )

    engine.say(text)

    try:
        engine.runAndWait()

    except Exception:
        pass

    try:
        engine.stop()

    except Exception:
        pass