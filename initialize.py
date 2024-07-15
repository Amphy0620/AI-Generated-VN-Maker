import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_gpt')
password = os.getenv('proxy_password')

def initialize(prompt, model):

    print("Initializing...")
    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "stream": True,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    response_content = ""
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
        promptOpener = sys.argv[1]
        prompt = sys.argv[2]
        prompt_modified = f"You're narrating a visual novel for the player; details and locations of this visual novel are provided here: {prompt} \n {promptOpener} \n First, choose a location among those provided for the player (using the exact locationName) to be initialized into the story as well as an initial time in 24 hour format (so 17:30 would represent 5:30 PM). Format this like so: On line 1, New location: locationName (exactly copied, without quotes). Then new line character \n, and on line 2, Current time: currentTime (again without quotes, in 24 hour format). Then new line character \n again, and on line 3, Current clothes: ... (give what the player is wearing at this time). Then \n again, and beginning with the fourth line, begin with Output: and then (still on line 4) become the narrator and introduce the player to the world. For example, New location: your_bedroom\nCurrent time: 07:40\nCurrent clothes: Boxer briefs\nOutput: Blah blah blah... [Try to keep this Output part under 400 characters.] Refer to the player in second person, as 'you', and give a modest description of the world they now find themselves in. The player should not be initialized around any characters; they should begin alone."
        model = sys.argv[3]
        response_data = initialize(prompt_modified, model)