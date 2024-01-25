
# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv

print(dir(openai))

print(openai.api_key)

audio_file= open(r"E:\test_rec.m4a", "rb")
transcript = client.audio.transcribe("whisper-1", audio_file)
print(transcript)
response = transcript.text
print(response)
