import speech_recognition as sr
import subprocess
import webbrowser
import os
import ctypes
import time
import threading

from memory import remember, recall, load_memory, save_memory
from ai import ask_ai
from voice import speak, stop_speaking, is_speaking
from ui_bridge import start_ui_server, set_ui_state


# =========================
# SPEECH RECOGNITION
# =========================

recognizer = sr.Recognizer()


def listen(current_state="active"):

    if current_state == "active":
        set_ui_state("listening")

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

        if current_state == "active":
            set_ui_state("thinking")

        return text.lower().strip()

    except sr.UnknownValueError:
        return None

    except sr.RequestError:
        return None

    except TimeoutError:
        return None


# =========================
# SWITCH SPEAKING
# =========================

speech_generation = 0


def switch_speak(text):

    global speech_generation

    speech_generation += 1
    current_generation = speech_generation

    set_ui_state("speaking")

    speak(text)

    def monitor():

        time.sleep(0.05)

        while True:

            if current_generation != speech_generation:
                return

            if not is_speaking():
                break

            time.sleep(0.05)

        if current_generation == speech_generation:
            set_ui_state("idle")

    threading.Thread(
        target=monitor,
        daemon=True
    ).start()


# =========================
# OPEN APPLICATION
# =========================

def open_application(text):

    apps = {

        "chrome": {
            "path": r"C:\Users\Public\Desktop\Google Chrome.lnk",
            "aliases": [
                "chrome",
                "google chrome",
                "browser"
            ]
        },

        "calculator": {
            "path": "calc.exe",
            "aliases": [
                "calculator",
                "calc"
            ]
        },

        "notepad": {
            "path": "notepad.exe",
            "aliases": [
                "notepad"
            ]
        },

        "file explorer": {
            "path": "explorer.exe",
            "aliases": [
                "file explorer",
                "explorer",
                "files"
            ]
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

                    try:

                        if app["path"].endswith(".lnk"):
                            os.startfile(app["path"])

                        else:
                            subprocess.Popen(
                                app["path"],
                                shell=True
                            )

                        switch_speak(f"Launching {app_name}.")

                    except Exception as e:

                        print("Application error:", e)

                        switch_speak(f"I couldn't open {app_name}.")

                    return True

    return False


# =========================
# CHROME CONTROLS
# =========================

def control_chrome(text):

    chrome_shortcut = (
        r"C:\Users\Public\Desktop"
        r"\Google Chrome.lnk"
    )

    chrome_path = (
        r"C:\Program Files\Google\Chrome"
        r"\Application\chrome.exe"
    )

    chrome_path_32 = (
        r"C:\Program Files (x86)\Google\Chrome"
        r"\Application\chrome.exe"
    )

    if "open new window" in text:

        try:

            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, "--new-window"])

            elif os.path.exists(chrome_path_32):
                subprocess.Popen([chrome_path_32, "--new-window"])

            else:
                os.startfile(chrome_shortcut)

            switch_speak("Opening a new Chrome window.")

        except Exception as e:

            print("Chrome error:", e)

            switch_speak("I couldn't open a new Chrome window.")

        return True

    if "open new tab" in text:

        try:

            if os.path.exists(chrome_path):
                subprocess.Popen([chrome_path, "--new-tab"])

            elif os.path.exists(chrome_path_32):
                subprocess.Popen([chrome_path_32, "--new-tab"])

            else:
                os.startfile(chrome_shortcut)

            switch_speak("Opening a new tab.")

        except Exception as e:

            print("Chrome error:", e)

            switch_speak("I couldn't open a new tab.")

        return True

    if (
        "open chrome" in text
        or "open google chrome" in text
        or "open browser" in text
    ):

        try:

            result = subprocess.run(
                [
                    "tasklist",
                    "/FI",
                    "IMAGENAME eq chrome.exe"
                ],
                capture_output=True,
                text=True
            )

            if "chrome.exe" in result.stdout:
                switch_speak("Chrome is already open.")

            else:
                os.startfile(chrome_shortcut)
                switch_speak("Opening Chrome.")

        except Exception as e:

            print("Chrome error:", e)

            switch_speak("I couldn't open Chrome.")

        return True

    return False


# =========================
# LAUNCH TARGETS
# =========================

def launch_target(text):

    targets = {

        "youtube": "https://www.youtube.com",

        "google": "https://www.google.com",

        "github": "https://github.com",

        "pinterest": "https://www.pinterest.com",

        "switch project": r"E:\switch-ai-assistance",

        "switch ai assistant": r"E:\switch-ai-assistance"
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

                try:

                    if target.startswith("http"):
                        webbrowser.open(target)

                    elif os.path.exists(target):
                        os.startfile(target)

                    else:
                        switch_speak(f"I couldn't find {target_name}.")
                        return True

                    switch_speak(f"Opening {target_name}.")

                except Exception as e:

                    print("Launch error:", e)

                    switch_speak(f"I couldn't open {target_name}.")

                return True

    return False


# =========================
# OPEN WEBSITE
# =========================

def open_website(text):

    websites = {

        "youtube": "https://www.youtube.com",

        "google": "https://www.google.com",

        "github": "https://github.com",

        "pinterest": "https://in.pinterest.com/"
    }

    for name, url in websites.items():

        if (
            text == name
            or f"open {name}" in text
            or f"launch {name}" in text
        ):

            webbrowser.open(url)

            switch_speak(f"Opening {name}.")

            return True

    return False


# =========================
# OPEN FOLDERS
# =========================

def open_folder(text):

    home = os.path.expanduser("~")

    folders = {

        "downloads": os.path.join(home, "Downloads"),

        "documents": os.path.join(home, "Documents"),

        "desktop": os.path.join(home, "Desktop"),

        "pictures": os.path.join(home, "Pictures"),

        "music": os.path.join(home, "Music"),

        "videos": os.path.join(home, "Videos"),

        "switch": r"E:\switch-ai-assistance",

        "switch ai assistant": r"E:\switch-ai-assistance"
    }

    for folder_name, folder_path in folders.items():

        if (
            f"open {folder_name}" in text
            or f"open my {folder_name}" in text
        ):

            if os.path.exists(folder_path):

                os.startfile(folder_path)

                switch_speak(f"Opening {folder_name}.")

            else:

                switch_speak(f"I couldn't find the {folder_name} folder.")

            return True

    return False


# =========================
# OPEN FILE
# =========================

def open_file(text):

    files = {

        "main": r"E:\switch-ai-assistance\main.py",

        "memory": r"E:\switch-ai-assistance\memory.py",

        "ai": r"E:\switch-ai-assistance\ai.py",

        "voice": r"E:\switch-ai-assistance\voice.py",

        "memory json": r"E:\switch-ai-assistance\memory.json"
    }

    for file_name, file_path in files.items():

        if (
            f"open {file_name}" in text
            or f"open the {file_name}" in text
        ):

            if os.path.exists(file_path):

                os.startfile(file_path)

                switch_speak(f"Opening {file_name}.")

            else:

                switch_speak(f"I couldn't find {file_name}.")

            return True

    return False


# =========================
# CONTROLLING PC
# =========================

def press_key(code):
    """Simulate a key press and release (used for media keys)."""
    ctypes.windll.user32.keybd_event(code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(code, 0, 2, 0)


def control_pc(text):

    # -------------------------
    # CLOSE CHROME
    # -------------------------

    if "close chrome" in text:

        subprocess.run(
            ["taskkill", "/IM", "chrome.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        switch_speak("Closing Chrome.")

        return True

    # -------------------------
    # CLOSE NOTEPAD
    # -------------------------

    if "close notepad" in text:

        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        switch_speak("Closing Notepad.")

        return True

    # -------------------------
    # CLOSE CALCULATOR
    # -------------------------

    if "close calculator" in text:

        subprocess.run(
            ["taskkill", "/IM", "CalculatorApp.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        switch_speak("Closing Calculator.")

        return True

    # -------------------------
    # VOLUME UP
    # -------------------------

    if (
        "volume up" in text
        or "increase volume" in text
    ):

        press_key(0xAF)

        switch_speak("Volume up.")

        return True

    # -------------------------
    # VOLUME DOWN
    # -------------------------

    if (
        "volume down" in text
        or "decrease volume" in text
    ):

        press_key(0xAE)

        switch_speak("Volume down.")

        return True

    # -------------------------
    # MUTE
    # -------------------------

    if text in ("mute", "mute volume", "mute the volume", "switch mute"):

        press_key(0xAD)

        switch_speak("Muted.")

        return True

    # -------------------------
    # LOCK COMPUTER
    # -------------------------

    if (
        "lock my pc" in text
        or "lock computer" in text
    ):

        switch_speak("Locking the computer.")

        ctypes.windll.user32.LockWorkStation()

        return True

    # -------------------------
    # SCREENSHOT
    # -------------------------

    if "screenshot" in text:

        screenshot_path = os.path.join(
            os.path.expanduser("~"),
            "Pictures",
            "SWITCH_screenshot.png"
        )

        powershell_command = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "Add-Type -AssemblyName System.Drawing; "
            "$screen = [System.Windows.Forms.Screen]::PrimaryScreen; "
            "$bitmap = New-Object System.Drawing.Bitmap "
            "$screen.Bounds.Width, $screen.Bounds.Height; "
            "$graphics = [System.Drawing.Graphics]::FromImage($bitmap); "
            "$graphics.CopyFromScreen("
            "$screen.Bounds.Location, "
            "[System.Drawing.Point]::Empty, "
            "$screen.Bounds.Size); "
            f"$bitmap.Save('{screenshot_path}')"
        )

        subprocess.run(
            [
                "powershell",
                "-Command",
                powershell_command
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        switch_speak("Screenshot taken.")

        return True

    # -------------------------
    # SHUT DOWN COMPUTER
    # -------------------------

    if text in (
        "power off the computer",
        "switch power off the computer",
        "shut down the computer",
        "switch off the computer"
    ):

        print("Powering off the computer...")

        switch_speak("Powering off the computer.")

        os.system("shutdown /s /t 0")

        return True

    return False


# =========================
# COMMAND PROCESSING
# =========================

def process_command(text):

    # -------------------------
    # SHOW MEMORIES
    # -------------------------

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
                memories.append(f"your {key} is {value}")

            response = "I remember that " + ", ".join(memories) + "."

    # -------------------------
    # FORGET MEMORY
    # -------------------------

    elif text.startswith("forget my "):

        key = text.replace("forget my ", "").strip()

        memory = load_memory()

        if key in memory:

            del memory[key]

            save_memory(memory)

            response = f"I forgot your {key}."

        else:

            response = f"I don't remember your {key}."

    # -------------------------
    # SAVE NAME
    # -------------------------

    elif "my name is" in text:

        name = text.replace("my name is", "").strip()

        remember("name", name)

        response = f"I'll remember that your name is {name}."

    # -------------------------
    # SAVE GENERAL MEMORY
    # -------------------------

    elif (
        text.startswith("my ")
        and " is " in text
    ):

        information = text[3:]

        key, value = information.split(" is ", 1)

        remember(key.strip(), value.strip())

        response = (
            f"I'll remember that your "
            f"{key.strip()} is {value.strip()}."
        )

    # -------------------------
    # REMEMBER THAT
    # -------------------------

    elif "remember that" in text:

        information = text.replace("remember that", "").strip()

        if " is " in information:

            key, value = information.split(" is ", 1)

            remember(key.strip(), value.strip())

            response = (
                f"I'll remember that your "
                f"{key.strip()} is {value.strip()}."
            )

        else:

            response = "Tell me what you want me to remember."

    # -------------------------
    # RECALL SPECIFIC MEMORY
    # -------------------------

    elif "do you remember my " in text:

        key = text.replace("do you remember my ", "").strip()

        value = recall(key)

        if value:
            response = f"Yes. Your {key} is {value}."

        else:
            response = f"I don't remember your {key}."

    # -------------------------
    # RECALL NAME
    # -------------------------

    elif (
        "what is my name" in text
        or "what's my name" in text
    ):

        name = recall("name")

        if name:
            response = f"Your name is {name}."

        else:
            response = "I don't know your name yet."

    # -------------------------
    # RECALL GENERAL MEMORY
    # -------------------------

    elif "what is my " in text:

        key = text.replace("what is my ", "").strip()

        value = recall(key)

        if value:
            response = f"Your {key} is {value}."

        else:
            response = f"I don't remember your {key}."

    # -------------------------
    # AI
    # -------------------------

    else:

        memory = load_memory()

        response = ask_ai(text, memory)

    print("SWITCH:", response)

    switch_speak(response)


# =========================
# MAIN
# =========================

def main():

    global speech_generation

    start_ui_server()

    set_ui_state("idle")

    print()
    print("==============================")
    print("        SWITCH ONLINE")
    print("==============================")
    print()

    switch_speak("How can I help you, master?")

    state = "active"

    while True:

        text = listen(state)

        if not text:
            continue

        # =========================
        # STOPPED MODE
        # =========================

        if state == "stopped":

            if (
                text == "wake up"
                or "wake up switch" in text
            ):

                state = "active"

                print("SWITCH is active.")

                set_ui_state("idle")

                switch_speak("Yes, master.")

            else:

                set_ui_state("idle")

            continue

        # =========================
        # SLEEPING MODE
        # =========================

        if state == "sleeping":

            if (
                text == "wake up"
                or "wake up switch" in text
            ):

                state = "active"

                print("SWITCH is active.")

                set_ui_state("idle")

                switch_speak("Yes, master.")

            else:

                set_ui_state("sleeping")

            continue

        # =========================
        # EXIT
        # =========================

        if (
            text == "exit"
            or text == "bye switch"
        ):

            speech_generation += 1

            stop_speaking()

            print("SWITCH is shutting off.")

            set_ui_state("exiting")

            switch_speak("Goodbye, Master.")

            time.sleep(3)

            break

        # =========================
        # STOP
        # =========================

        if (
            text == "stop"
            or text == "stop switch"
            or text == "switch stop"
            or text == "stop listening"
            or "stop listening switch" in text
        ):

            speech_generation += 1

            stop_speaking()

            state = "stopped"

            print("SWITCH is stopped.")

            set_ui_state("idle")

            continue

        # =========================
        # SLEEP
        # =========================

        if (
            text == "go to sleep"
            or text == "sleep"
            or "go to sleep switch" in text
            or "switch to sleep" in text
        ):

            speech_generation += 1

            state = "sleeping"

            print("SWITCH is sleeping.")

            set_ui_state("sleeping")

            switch_speak("Going to sleep.")

            set_ui_state("sleeping")

            continue

        # =========================
        # PC CONTROLS
        # =========================

        if control_pc(text):
            continue

        # =========================
        # CHROME CONTROLS
        # =========================

        if control_chrome(text):
            continue

        # =========================
        # APPLICATIONS
        # =========================

        if open_application(text):
            continue

        # =========================
        # LAUNCH TARGETS
        # =========================

        if launch_target(text):
            continue

        # =========================
        # WEBSITES
        # =========================

        if open_website(text):
            continue

        # =========================
        # FOLDERS
        # =========================

        if open_folder(text):
            continue

        # =========================
        # FILES
        # =========================

        if open_file(text):
            continue

        # =========================
        # AI
        # =========================

        process_command(text)


# =========================
# START SWITCH
# =========================

if __name__ == "__main__":
    main()