import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_claude')
password = os.getenv('proxy_password')

def process_json_array(json_array):
    # Step 1: Change "system" roles to "user" with content encapsulated
    for item in json_array:
        if item['role'] == 'system':
            item['role'] = 'user'
            item['content'] = f"[System message: {item['content']}]"
    
    # Step 2: Merge adjacent dictionaries with the same role
    processed_array = []
    current_role = None
    current_content = []

    for item in json_array:
        if item['role'] == current_role:
            current_content.append(item['content'])
        else:
            if current_role is not None:
                processed_array.append({
                    'role': current_role,
                    'content': '\n'.join(current_content)
                })
            current_role = item['role']
            current_content = [item['content']]

    if current_role is not None:
        processed_array.append({
            'role': current_role,
            'content': '\n'.join(current_content)
        })

    return processed_array

def initialize(prompt, model):

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    inputArray = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "New location:"}
    ]

    data = {
        "model": model,
        "system": "You are a helpful assistant.",
        "max_tokens": 4096,
        "stream": True,
        "messages": process_json_array(inputArray)
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    response_content = "New location:"

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

if __name__ == "__main__":
    if len(sys.argv) > 3:
        promptOpener = sys.argv[1]
        prompt = sys.argv[2]
        prompt_modified = f"You're narrating a visual novel for the player; details and locations of this visual novel are provided here: {prompt} \n {promptOpener} \n First, choose a location among those provided for the player (using the exact locationName) to be initialized into the story as well as an initial time in 24 hour format (so 17:30 would represent 5:30 PM). Format this like so: On line 1, New location: locationName (exactly copied, without quotes). Then new line character \n, and on line 2, Current time: currentTime (again without quotes, in 24 hour format). Then new line character \n again, and on line 3, Current clothes: ... (give what the player is wearing at this time). Then \n again, and beginning with the fourth line, begin with Output: and then (still on line 4) become the narrator and introduce the player to the world. For example, New location: your_bedroom\nCurrent time: 07:40\nCurrent clothes: Boxer briefs\nOutput: Blah blah blah... [Try to keep this Output part under 400 characters.] Refer to the player in second person, as 'you', and give a modest description of the world they now find themselves in. The player should not be initialized around any characters; they should begin alone."
        model = sys.argv[3]
        response_data = initialize(prompt_modified, model)