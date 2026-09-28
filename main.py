import speech_recognition as sr
import subprocess
import webbrowser
import os
import ctypes

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
    
        return None

    except sr.RequestError:

        return None

    except TimeoutError:

        return None


## OPEN APPLICATION ##

def open_application(text):

    apps = {
        "chrome": {
            "path": r"C:\Users\Public\Desktop\Google Chrome.lnk",
            "aliases": ["chrome", "google chrome", "browser"]
        },

        "calculator": {
            "path": "calc.exe",
            "aliases": ["calculator", "calc"]
        },

        "notepad": {
            "path": "notepad.exe",
            "aliases": ["notepad"]
        },

        "file explorer": {
            "path": "explorer.exe",
            "aliases": ["file explorer", "explorer", "files"]
        },

        "vs code": {
            "path": "code",
            "aliases": [
                "vs code",
                "visual studio code",
                "vscode"
            ]
        }
    }

    launch_words = [
        "open",
        "launch",
        "start",
        "run",
        "bring up"
    ]

    for app_name, app in apps.items():

        for alias in app["aliases"]:

            for launch_word in launch_words:

                if f"{launch_word} {alias}" in text:

                    if app["path"].endswith(".lnk"):
                        os.startfile(app["path"])
                    else:
                        subprocess.Popen(
                            app["path"],
                            shell=True
                        )

                    speak(f"Launching {app_name}.")
                    return True

    return False

## CONTROLING CHROME
def control_chrome(text):

    chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    if "open new window" in text:
        subprocess.Popen(
            [chrome_path, "--new-window"]
        )
        speak("Opening a new Chrome window.")
        return True

    if "open new tab" in text:
        subprocess.Popen(
            [chrome_path, "--new-tab"]
        )
        speak("Opening a new tab.")
        return True

    if (
        "open chrome" in text
        or "open google chrome" in text
        or "open browser" in text
    ):
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True,
            text=True
        )

        if "chrome.exe" in result.stdout:
            speak("Chrome is already open.")
        else:
            os.startfile(
                r"C:\Users\Public\Desktop\Google Chrome.lnk"
            )
            speak("Opening Chrome.")

        return True

    return False

## COMBINED COMMANDS ##
def launch_target(text):

    targets = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "pinterest": "https://www.pinterest.com",

        "switch project": r"E:\switch-ai-assistance",
        "switch ai assistant": r"E:\switch-ai-assistance",
    }

    launch_words = [
        "open",
        "launch",
        "start",
        "bring up"
    ]

    for target_name, target in targets.items():

        for launch_word in launch_words:

            if f"{launch_word} {target_name}" in text:

                if target.startswith("http"):
                    webbrowser.open(target)
                else:
                    if os.path.exists(target):
                        os.startfile(target)

                speak(f"Opening {target_name}.")
                return True

    return False


## OPEN WEBSITE ##
def open_website(text):

    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://github.com",
        "pinterest": "https://in.pinterest.com/"
    }

    for name, url in websites.items():

        if name in text:

            webbrowser.open(url)

            speak(f"Opening {name}.")
            return True

    return False


## OPEN FOLDERS ##


def open_folder(text):

    folders = {
        "downloads": os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        ),

        "documents": os.path.join(
            os.path.expanduser("~"),
            "Documents"
        ),

        "desktop": os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        ),

        "pictures": os.path.join(
            os.path.expanduser("~"),
            "Pictures"
        ),

        "music": os.path.join(
            os.path.expanduser("~"),
            "Music"
        ),

        "videos": os.path.join(
            os.path.expanduser("~"),
            "Videos"
        ),

        "switch": r"E:\switch-ai-assistance",
        "switch ai assistant": r"E:\switch-ai-assistance",
    }

    for folder_name, folder_path in folders.items():

        if (
            f"open {folder_name}" in text
            or f"open my {folder_name}" in text
        ):

            if os.path.exists(folder_path):

                os.startfile(folder_path)

                speak(
                    f"Opening {folder_name}."
                )

                return True

    return False


def open_file(text):

    files = {
        "main": r"E:\switch-ai-assistance\main.py",
        "memory": r"E:\switch-ai-assistance\memory.py",
        "ai": r"E:\switch-ai-assistance\ai.py",
        "voice": r"E:\switch-ai-assistance\voice.py",
        "memory": r"E:\switch-ai-assistance\memory.json",
    }

    for file_name, file_path in files.items():

        if (
            f"open {file_name}" in text
            or f"open the {file_name}" in text
        ):

            if os.path.exists(file_path):

                os.startfile(file_path)

                speak(
                    f"Opening {file_name}."
                )

                return True

    return False


##  CONTROLING PC ##


def control_pc(text):

    if "close chrome" in text:
        subprocess.run(
            ["taskkill", "/IM", "chrome.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        speak("Closing Chrome.")
        return True

    if "close notepad" in text:
        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        speak("Closing Notepad.")
        return True

    if "close calculator" in text:
        subprocess.run(
            ["taskkill", "/IM", "CalculatorApp.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        speak("Closing Calculator.")
        return True

    if "volume up" in text or "increase volume" in text:
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        speak("Volume up.")
        return True

    if "volume down" in text or "decrease volume" in text:
        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
        speak("Volume down.")
        return True

    if "mute" in text:
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        speak("Muted.")
        return True

    if "lock my pc" in text or "lock computer" in text:
        speak("Locking the computer.")
        ctypes.windll.user32.LockWorkStation()
        return True

    if "take a screenshot" in text or "screenshot" in text:
        screenshot_path = os.path.join(
            os.path.expanduser("~"),
            "Pictures",
            "SWITCH_screenshot.png"
        )

        subprocess.run(
            [
                "powershell",
                "-Command",
                "Add-Type -AssemblyName System.Windows.Forms; "
                "Add-Type -AssemblyName System.Drawing; "
                "$screen = [System.Windows.Forms.Screen]::PrimaryScreen; "
                "$bitmap = New-Object System.Drawing.Bitmap "
                "$screen.Bounds.Width, $screen.Bounds.Height; "
                "$graphics = [System.Drawing.Graphics]::FromImage($bitmap); "
                "$graphics.CopyFromScreen("
                "$screen.Bounds.Location, "
                "[System.Drawing.Point]::Empty, "
                "$screen.Bounds.Size"
                "); "
                f"$bitmap.Save('{screenshot_path}')"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        speak("Screenshot taken.")
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

# =========================
# MAIN
# =========================

def main():

    print()
    print("==============================")
    print("        SWITCH ONLINE")
    print("==============================")
    print()

    speak("How can I help you, master?")

    state = "active"

    while True:

        text = listen()

        if not text:
            continue

        # =========================
        # STOPPED MODE
        # =========================

        if state == "stopped":

            # Only wake up works while stopped
            if (
                text == "wake up"
                or "wake up switch" in text
            ):
                state = "active"

                print("SWITCH is active.")

                speak("Yes, master.")

            continue

        # =========================
        # SLEEPING MODE
        # =========================

        if state == "sleeping":

            # Only wake up works while sleeping
            if (
                text == "wake up"
                or "wake up switch" in text
            ):
                state = "active"

                print("SWITCH is active.")

                speak("Yes, master.")

            continue

        # =========================
        # ACTIVE MODE
        # =========================

        # EXIT
        if text == "exit":
            print("SWITCH is shutting off.")
            speak("SWITCH is shutting off.")
            break

        # STOP
        if (
            text == "stop"
            or text == "stop switch"
            or text == "switch stop"
            or text == "stop listening"
            or "stop listening switch" in text
        ):
            state = "stopped"

            print("SWITCH is stopped.")

            speak("Stopping. Say wake up when you need me.")

            continue

        # SLEEP
        if (
            text == "go to sleep"
            or text == "sleep"
            or "go to sleep switch" in text
            or "switch to sleep" in text
        ):
            state = "sleeping"

            print("SWITCH is sleeping.")

            speak("Going to sleep.")

            continue
        
        # PC CONTROLS
        if control_pc(text):
            continue

        # CHROME CONTROLS
        if control_chrome(text):
            continue

        # APPLICATIONS
        if open_application(text):
            continue

        # LAUNCH TARGETS
        if launch_target(text):
            continue

        # WEBSITES
        if open_website(text):
            continue

        # FOLDERS
        if open_folder(text):
            continue

        # FILES
        if open_file(text):
            continue

        # AI
        process_command(text)


# START SWITCH

if __name__ == "__main__":
    main()