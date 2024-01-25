# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
from openai import OpenAI

client = OpenAI()

audio_file= open(r"E:\test_audio_2.mp3", "rb")
transcript = client.audio.transcribe("whisper-1", audio_file)
print(transcript)
response = transcript.text
print(response)