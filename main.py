import speech_recognition as sr
import subprocess

from memory import remember, recall, load_memory, save_memory
from ai import ask_ai
from voice import speak


# =========================
# SPEECH RECOGNITION
# =========================

recognizer = sr.Recognizer()


def listen():

    with sr.Microphone() as source:

        print("SWITCH is listening...")

        try:

            audio = recognizer.listen(
                source,
                timeout=None,
                phrase_time_limit=None
            )

        except sr.WaitTimeoutError:

            return None

    try:

        text = recognizer.recognize_google(audio)

        print("You:", text)

        return text.lower().strip()

    except sr.UnknownValueError:

        # Stay silent if speech isn't understood
        return None

    except sr.RequestError as error:

        print(
            "Speech recognition service error:",
            error
        )

        return None


## OPEN APPLICATION ##

def open_application(text):

    apps = {
        "chrome": r"C:\Users\Public\Desktop\Google Chrome.lnk",
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "file explorer": "explorer.exe",
        "vs code": "code"
    }

    for app_name, command in apps.items():

        if f"open {app_name}" in text:

            subprocess.Popen(
                command,
                shell=True
            )

            speak(f"Opening {app_name}.")
            return True

    return False


# =========================
# COMMAND PROCESSING
# =========================

def process_command(text):

    if (
        "what do you remember about me" in text
        or "what do you remember" in text
        or "show my memories" in text
        or "show all memories" in text
    ):

        memory = load_memory()

        if not memory:

            response = "I don't have any memories saved yet."

        else:

            memories = []

            for key, value in memory.items():

                memories.append(
                    f"your {key} is {value}"
                )

            response = (
                "I remember that "
                + ", ".join(memories)
                + "."
            )

    elif text.startswith("forget my "):

        key = text.replace(
            "forget my ",
            ""
        ).strip()

        memory = load_memory()

        if key in memory:

            del memory[key]
            save_memory(memory)

            response = f"I forgot your {key}."

        else:

            response = f"I don't remember your {key}."

    elif "my name is" in text:

        name = text.replace(
            "my name is",
            ""
        ).strip()

        remember(
            "name",
            name
        )

        response = (
            f"I'll remember that your name is {name}."
        )

    elif text.startswith("my ") and " is " in text:

        information = text[3:]

        key, value = information.split(
            " is ",
            1
        )

        remember(
            key.strip(),
            value.strip()
        )

        response = (
            f"I'll remember that your "
            f"{key.strip()} is {value.strip()}."
        )

    elif "remember that" in text:

        information = text.replace(
            "remember that",
            ""
        ).strip()

        if " is " in information:

            key, value = information.split(
                " is ",
                1
            )

            remember(
                key.strip(),
                value.strip()
            )

            response = (
                f"I'll remember that your "
                f"{key.strip()} is {value.strip()}."
            )

        else:

            response = (
                "Tell me what you want me to remember."
            )

    elif "do you remember my " in text:

        key = text.replace(
            "do you remember my ",
            ""
        ).strip()

        value = recall(key)

        if value:

            response = (
                f"Yes. Your {key} is {value}."
            )

        else:

            response = (
                f"I don't remember your {key}."
            )

    elif (
        "what is my name" in text
        or "what's my name" in text
    ):

        name = recall("name")

        if name:

            response = f"Your name is {name}."

        else:

            response = "I don't know your name yet."

    elif "what is my " in text:

        key = text.replace(
            "what is my ",
            ""
        ).strip()

        value = recall(key)

        if value:

            response = f"Your {key} is {value}."

        else:

            response = (
                f"I don't remember your {key}."
            )

    else:

        memory = load_memory()

        response = ask_ai(
            text,
            memory
        )

    print("SWITCH:", response)

    speak(response)


# =========================
# MAIN
# =========================

def main():

    print()
    print("==============================")
    print("        SWITCH ONLINE")
    print("==============================")
    print()

    speak(
        "How's the day going, Sam?"
    )

    state = "active"

    while True:

        text = listen()

        if not text:
            continue

        # =========================
        # STOPPED MODE
        # =========================

        if state == "stopped":

            if text == "exit":

                speak(
                    "SWITCH is shutting off."
                )

                print(
                    "SWITCH is shutting off."
                )

                break

            if (
                text == "wake up"
                or "wake up switch" in text
            ):

                state = "active"

                print(
                    "SWITCH is active."
                )

                speak(
                    "Yes, master."
                )

                continue

            continue

        # =========================
        # SLEEPING MODE
        # =========================

        if state == "sleeping":

            if text == "exit":

                speak(
                    "SWITCH is shutting off."
                )

                print(
                    "SWITCH is shutting off."
                )

                break

            if (
                text == "wake up"
                or "wake up switch" in text
            ):

                state = "active"

                print(
                    "SWITCH is active."
                )

                speak(
                    "Yes, master."
                )

                continue

            # Ignore everything else
            continue

        # =========================
        # ACTIVE MODE
        # =========================

        if text == "exit":

            speak(
                "SWITCH is shutting off."
            )

            print(
                "SWITCH is shutting off."
            )

            break

        if text == "stop":

            state = "stopped"

            print(
                "SWITCH is stopped."
            )

            continue

        if (
            text == "go to sleep"
            or text == "sleep"
            or "switch to sleep" in text
        ):

            state = "sleeping"

            print(
                "SWITCH is sleeping."
            )

            speak(
                "Going to sleep."
            )

            continue
    # Computer commands
        if open_application(text):
            continue
        
        # Normal command
        process_command(text)


# =========================
# START SWITCH
# =========================

if __name__ == "__main__":

    main()