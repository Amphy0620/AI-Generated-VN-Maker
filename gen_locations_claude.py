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

def gen_locations(prompt, output_dir, jailbreak, model):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    inputArray = [
        {"role": "user", "content": prompt},
        {"role": "system", "content": jailbreak},
        {"role": "assistant", "content": "["}
    ]

    data = {
        "model": model,
        "system": "You are a helpful assistant.",
        "max_tokens": 4096,
        "stream": True,
        "messages": process_json_array(inputArray)
    }

    response = requests.post(url, headers=headers, json=data, stream=True)
    response_content = "["

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

        with open(output_path / "locations.txt", "w") as f:
            f.write(response_content)

if __name__ == "__main__":

    if len(sys.argv) > 4:
        with open(sys.argv[1], 'r') as f:
            prompt = f.read()
        prompt_modified = f"We're creating a visual novel world based on the following world info and characters: {prompt} \n Output a JSON file which gives an array of locations for the player and character to move around. Each location should have attributes \"locationNumber\", \"locationName\", \"locationTextDescription\", \"locationTagDescription\", \"adjacentLocations\", \"isHubArea\" and \"isOutdoors\". isOutdoors really asks whether we need separate images for day and night skies; in weird or ambiguous cases like outer space, default to no. locationNumber starts at 1 and increments with each location. locationTextDescription briefly (no more than a sentence) describes the location in prose. locationTagDescription should be a brief list of objects and features of the location; for example, a bedroom might have \"bed, cabinet, tv\", a swimming pool might just have \"swimming pool\", an orbital space station might have \"planet, stars\"... essentially consider the list of objects the player should see at each location. These should be brief and only hit the essentials. adjacentLocations should be an array consisting of strings of other locationNames reachable from the current location; make the world somewhat interconnected, don't isolate locations too much! isHubArea is a boolean denoting whether that area is potentially a major crossroads at which the player can reach other hub areas; for example, if the setting is a small city, \"Downtown\" and \"Residential District\" might be hub areas, but not \"Classroom\" or \"Beach\". Important: Spread out connections over several hub areas; the bigger the world, the more hub areas. isOutdoors is a true or false boolean. When creating locations, consider not just the world itself but the characters inhabiting it; where might they go and what might they do? In particular, each character should have their own house or other living quarters (unless the scenario contradicts that). Don't forget to give the player their own place too (if necessary). Be exhaustive; for example, a small town might have a school with many different rooms, a residential area with everyone's house, a downtown with many businesses, a park, and so on. Building interiors should also have a realistic variety of rooms; standard living spaces have bathrooms and bedrooms; schools especially have club rooms, classrooms, gyms, so on. Modern personal living spaces should have a separate bathroom, if applicable. Less detailed worlds might have fewer locations (a deserted island, for instance), but you should still come up with a lot. You should be giving at least several dozen locations. Consider all parts of the characters' day; where do they sleep? Where do they shower? Work, play, go out? Fill out the world with both practical locations and fun 'extra' locations. All locations should have at least one adjacent location; try to make the world fully connected. DON'T include backticks or 'json' formatting, just the raw json output."
        output_dir = sys.argv[2]
        with open(sys.argv[3], 'r') as f:
            jailbreak = f.read()
        model = sys.argv[4]
        response_data = gen_locations(prompt_modified, output_dir, jailbreak, model)