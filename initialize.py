import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_gpt')
password = os.getenv('proxy_password')

from basic_functions import process_json_array
from prompts import initialize_prompt

def initialize(prompt, model):

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    isClaude = (model[:6] == "claude")

    inputArray = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    data = {
        "model": model,
        "stream": True,
        "messages": inputArray,
        "max_tokens": 4096
    }

    if isClaude:
        inputArray.append({"role": "assistant", "content": "New location:"})
        inputArray = process_json_array(inputArray)
        data['messages'] = inputArray
        data['max_tokens'] = 4096
        url = os.getenv('proxy_url_claude')

    else:
        url = os.getenv('proxy_url_gpt')        
        
    response = requests.post(url, headers=headers, json=data)
    response_content = ""
    if isClaude:
        response_content = "New location:"

    if isClaude:
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    event_data = line[6:]  # Remove "data: " prefix
                    try:
                        json_data = json.loads(event_data)
                        if 'text' in json_data.get('delta', {}):
                            response_content += json_data['delta']['text']
                    except json.JSONDecodeError:
                        continue

            print(response_content)
            return response_content

    else:
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data: "):
                        event_data = line[6:]  # Remove "data: " prefix
                        if event_data.strip() == "[DONE]":
                            break
                        try:
                            json_data = json.loads(event_data)
                            if 'choices' in json_data:
                                delta = json_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    response_content += delta['content']
                        except json.JSONDecodeError:
                            continue

            print(response_content)
            return response_content

if __name__ == "__main__":
    if len(sys.argv) > 3:
        playerInfo = sys.argv[1]
        worldInfo = sys.argv[2]
        prompt_modified = initialize_prompt(worldInfo, playerInfo)
        model = sys.argv[3]
        response_data = initialize(prompt_modified, model)