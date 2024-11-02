import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_gpt')
password = os.getenv('proxy_password')

from basic_functions import process_json_array
from prompts import gen_world_prompt

def gen_world(prompt, output_dir, jailbreak, model):
    print("We're here!")
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    isClaude = (model[:6] == "claude")

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    inputArray = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
        {"role": "system", "content": jailbreak}
    ]

    data = {
        "model": model,
        "stream": True,
        "messages": inputArray,
        "max_tokens": 4096
    }

    if isClaude:
#        inputArray.append({"role": "assistant", "content": "{"})
        inputArray = process_json_array(inputArray)
        data['messages'] = inputArray
        data['max_tokens'] = 4096
        url = os.getenv('proxy_url_claude')

#    else:
#        url = os.getenv('proxy_url_gpt')     
        
    response = requests.post(url, headers=headers, json=data)
    response_content = ""

#    if isClaude:
#        response_content = "{"

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

            with open(output_path / "world_0.txt", "w") as f:
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

            with open(output_path / "world_0.txt", "w") as f:
                f.write(response_content)

if __name__ == "__main__":
    if len(sys.argv) == 9:
        with open(sys.argv[1], 'r') as f:
            playerInput = f.read()
        output_dir = sys.argv[2]
        with open(sys.argv[3], 'r') as f:
            jailbreak = f.read()
        numMales = sys.argv[4]
        numFemales = sys.argv[5]
        model = sys.argv[6]
        clothingLabelsStr = sys.argv[7]
        isCharWorkClothes = sys.argv[8]
        prompt_modified = gen_world_prompt(playerInput, clothingLabelsStr, isCharWorkClothes)
        prompt_modified += f" Begin with exactly {numMales} male characters and {numFemales} female characters in this output."
        response_data = gen_world(prompt_modified, output_dir, jailbreak, model)

    else:
        with open(sys.argv[2], 'r') as f:
            playerInput = f.read()
        output_dir = sys.argv[3]
        with open(sys.argv[4], 'r') as f:
            jailbreak = f.read()
        numMales = sys.argv[5]
        numFemales = sys.argv[6]
        model = sys.argv[7]
        clothingLabelsStr = sys.argv[8]
        isCharWorkClothes = sys.argv[9]
        prompt_modified = gen_world_prompt(playerInput, clothingLabelsStr, isCharWorkClothes)
        prompt_modified += f" Begin with exactly {numMales} male characters and {numFemales} female characters in this output."
        response_data = gen_world(prompt_modified, output_dir, jailbreak, model)
