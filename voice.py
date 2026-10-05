import pyttsx3
import threading


_engine = None
_engine_lock = threading.Lock()
_speaking = False


def _speak_worker(text):
    global _engine
    global _speaking

    engine = None

    try:
        engine = pyttsx3.init()

        voices = engine.getProperty("voices")

        if len(voices) > 1:
            engine.setProperty(
                "voice",
                voices[1].id
            )

        engine.setProperty(
            "rate",
            145
        )

        engine.setProperty(
            "volume",
            1.0
        )

        with _engine_lock:
            _engine = engine

        engine.say(text)

        try:
            engine.runAndWait()
        except Exception:
            pass

    except Exception:
        pass

    finally:
        try:
            if engine is not None:
                engine.stop()
        except Exception:
            pass

        with _engine_lock:

            if _engine is engine:
                _engine = None

            _speaking = False


def speak(text):
    """
    Start speech in the background.
    Mark speaking immediately so the UI
    cannot miss the speaking state.
    """

    global _speaking

    with _engine_lock:
        _speaking = True

    thread = threading.Thread(
        target=_speak_worker,
        args=(text,),
        daemon=True
    )

    thread.start()


def stop_speaking():
    """
    Immediately stop current speech.
    """

    global _engine
    global _speaking

    with _engine_lock:
        engine = _engine
        _speaking = False

    if engine is not None:
        try:
            engine.stop()
        except Exception:
            pass


def is_speaking():
    with _engine_lock:
        return _speaking