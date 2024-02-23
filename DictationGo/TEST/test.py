import argparse
import json
import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.websocket import AudioSource

APIKEY = 'yhjoY__LBY7AAwvaaDS_1NNjn5tTfPzbfcKNerPEeevH'
APIURL = 'https://api.us-east.speech-to-text.watson.cloud.ibm.com/instances/a6705c72-fa12-4f0f-ae33-5dd847f2786e'


from ibm_watson.websocket import AudioSource

# Define the corrected AudioSource class
class MyAudioSource(AudioSource):
    def __init__(self, audio_data, is_final=False):
        super().__init__(enable_multithread=True)
        self.audio_data = audio_data
        self.is_final = is_final
        self.position = 0

    def get_audio_data(self, **kwargs):
        return [self.audio_data]

    def settings(self):
        return {
            'format': 'lpcm',
            'channels': 1,
            'rate': 44100
        }

    def read(self, size):
        chunk = self.audio_data[self.position:self.position + size]
        self.position += len(chunk)
        return chunk

# Function to record audio from microphone
def record_audio(duration):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("* Recording audio...")

    frames = []
    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_data = b''.join(frames)
    audio_source = MyAudioSource(audio_data)

    return audio_source

# Rest of your code...


# Function to connect to Watson Speech to Text service and transcribe audio
def transcribe_audio(audio_data, timeout):
    authenticator = IAMAuthenticator(APIKEY)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(APIURL)

    class MyRecognizeCallback(RecognizeCallback):
        def on_data(self, data):
            print(json.dumps(data, indent=2))

        def on_error(self, error):
            print('Error received: {}'.format(error))

        def on_inactivity_timeout(self, error):
            print('Inactivity timeout: {}'.format(error))

    myRecognizeCallback = MyRecognizeCallback()

    audio_source = AudioSource(audio_data)

    speech_to_text.recognize_using_websocket(
        audio=audio_source,
        content_type='audio/l16;rate=44100',
        recognize_callback=myRecognizeCallback,
        interim_results=True
    )

# Main function
def main():
    parser = argparse.ArgumentParser(description='Transcribe audio from microphone using Watson Speech to Text')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout for recording in seconds')
    args = parser.parse_args()

    # Record audio from microphone
    audio_data = record_audio(args.timeout)

    # Transcribe audio using Watson Speech to Text
    transcribe_audio(audio_data, args.timeout)

if __name__ == "__main__":
    main()
