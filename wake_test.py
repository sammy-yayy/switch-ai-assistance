from wake import detect_double_clap
from voice import speak


print("SWITCH wake system starting...")

if detect_double_clap():

    print("SWITCH detected the double clap!")

    speak("Yes, master. I'm listening.")