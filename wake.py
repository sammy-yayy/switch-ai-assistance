import pyaudio
import audioop
import time


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 512

CLAP_THRESHOLD = 2500


def detect_double_clap():

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    clap_count = 0
    last_clap_time = 0

    try:

        while True:

            data = stream.read(
                CHUNK,
                exception_on_overflow=False
            )

            volume = audioop.rms(data, 2)
            current_time = time.time()

            if volume > CLAP_THRESHOLD:

                if current_time - last_clap_time > 0.20:

                    clap_count += 1
                    last_clap_time = current_time

                    if clap_count == 2:
                        return True

            if clap_count == 1:

                if current_time - last_clap_time > 1.2:
                    clap_count = 0

    finally:

        stream.stop_stream()
        stream.close()
        audio.terminate()