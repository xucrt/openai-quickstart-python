
# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
#import os
import openai

#print(dir(openai))
#openai.api_key = os.getenv("OPENAI_API_KEY")

audio_file= open(r"E:\test_rec.m4a", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)
response = transcript.text
print(response)
