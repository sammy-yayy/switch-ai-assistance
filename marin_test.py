import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


speech_file_path = Path("marin_test.mp3")

response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="marin",
    input="Hey Sam. How's your day going?",
    instructions=(
        "Speak like a warm, intelligent female AI assistant. "
        "Use a soft, elegant and natural tone. "
        "Be friendly and emotionally expressive, "
        "with subtle cinematic warmth. "
        "Speak calmly and naturally, never robotic."
    )
)

response.write_to_file(speech_file_path)

print("Marin voice test created.")