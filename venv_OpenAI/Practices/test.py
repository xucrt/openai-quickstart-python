import os
import openai

#openai.api_key = os.getenv("E:\Programs\Git\OpenAI\openai-quickstart-python\.env")
#openai.api_key = "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"
#openai.api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Say this is a test",
    temperature=0,
    max_tokens=5
)

print(response)


"""
C# / .NET
Crystal
Go
Java
Kotlin
Node.js
PHP
Python
R
Ruby
Scala
Swift
Unity
Unreal Engine

24个库
"""

