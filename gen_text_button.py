import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_claude')
password = os.getenv('proxy_password')

from basic_functions import process_json_array
from prompts import button_input_instructions

def gen_text_button(promptJSON, model, jailbreak, prefill, boolRomanticProgression, clothingNamesStr, emotionNamesStr):

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    isClaude = (model[:6] == "claude")

    instructions = button_input_instructions(boolRomanticProgression, clothingNamesStr, emotionNamesStr)

    promptJSON.append({"role": "system", "content": instructions})

    if len(jailbreak) > 0:
        promptJSON.append({"role": "system", "content": jailbreak})
    if isClaude and len(prefill) > 0:
        promptJSON.append({"role": "assistant", "content": prefill})

    data = {
        "model": model,
        "stream": True,
        "messages": promptJSON,
        "max_tokens": 4096
    }

    if isClaude:
        data['max_tokens'] = 4096
        data['messages'] = process_json_array(promptJSON)
        url = os.getenv('proxy_url_claude')

    else:
        url = os.getenv('proxy_url_gpt')

    response = requests.post(url, headers=headers, json=data, stream=True)
    response_content = ""
        
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

            return response_content

if __name__ == "__main__":
    if len(sys.argv) > 7:
        file_path = sys.argv[1]
        with open(file_path, 'r') as f:
            promptJSON = json.load(f)
        model = sys.argv[2]
        jailbreak = sys.argv[3]
        prefill = sys.argv[4]
        boolRomanticProgression = sys.argv[5]
        clothingNamesStr = sys.argv[6]
        emotionNamesStr = sys.argv[7]
        response_data = gen_text_button(promptJSON, model, jailbreak, prefill, boolRomanticProgression, clothingNamesStr, emotionNamesStr)
        print(response_data)
