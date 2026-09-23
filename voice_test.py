import asyncio
import edge_tts


async def main():

    text = "Hey Sam. How's your day going?"

    voice = "en-US-AriaNeural"

    communicate = edge_tts.Communicate(
        text,
        voice
    )

    await communicate.save("voice_test.mp3")


asyncio.run(main())

print("Voice test created.")