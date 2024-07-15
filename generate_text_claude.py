import anthropic
import requests
import sys
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key="68a4f438-9c35-45c1-84d3-a4944d7f484e")
client.base_url = "https://vip.jewproxy.tech/proxy/aws/claude/v1"

completion = client.chat.completions.create(
  model="claude-3-5-sonnet-20240620",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write me a delectably raunchy poem."}
  ]
)

print(completion.choices[0].message.content)