import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_gpt')
password = os.getenv('proxy_password')

from basic_functions import process_json_array
from prompts import gen_location_prompt

def gen_locations(prompt, output_dir, jailbreak, model):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    isClaude = (model[:6] == "claude")

    inputArray = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
        {"role": "system", "content": jailbreak}
    ]

    data = {
        "model": model,
        "stream": True,
        "messages": inputArray
    }

    if isClaude:
        inputArray.append({"role": "assistant", "content": "["})
        inputArray = process_json_array(inputArray)
        data['messages'] = inputArray
        data['max_tokens'] = 4096
        url = os.getenv('proxy_url_claude')

    else:
        url = os.getenv('proxy_url_gpt')        
        
    response = requests.post(url, headers=headers, json=data)
    response_content = ""
    if isClaude:
        response_content = "["

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

            with open(output_path / "locations_temp.txt", "w") as f:
                f.write(response_content)

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

            with open(output_path / "locations_temp.txt", "w") as f:
                f.write(response_content)

if __name__ == "__main__":

    if len(sys.argv) > 6:
        with open(sys.argv[1], 'r') as f:
            worldInfo = f.read()
        output_dir = sys.argv[2]
        with open(sys.argv[3], 'r') as f:
            jailbreak = f.read()
        model = sys.argv[4]
        finalLocationInThisGen = sys.argv[5]
        isContinuation = sys.argv[6]
        previousLocations = ""
        if len(sys.argv) > 7:
            with open(sys.argv[7], 'r') as f:
                previousLocations = f.read()
        prompt_modified = gen_location_prompt(worldInfo, isContinuation, previousLocations)
        prompt_modified += f"You must stop exactly at location number {finalLocationInThisGen} in this output; you should generate up to this locationNumber and then stop."
        response_data = gen_locations(prompt_modified, output_dir, jailbreak, model)

