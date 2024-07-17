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

def gen_text_prompt(promptJSON, model, jailbreak, prefill, boolRomanticProgression):

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    isClaude = (model[:6] == "claude")

    romanceInstructions = ""
    romanceExample = ""
    if boolRomanticProgression == "True":
        romanceInstructions = " Furthermore, given the most recent interaction, for each character the player interacted with, on a new line, give an Interaction Intimacy Rating from 0 to 10 formatted like this: \nInteraction Intimacy Rating X: Y\n where X is again the relevant character number and Y is the rating. Use the following as a rough guide for what score to give:\n0: Negative interaction/No direct interaction.\n2: Polite conversation (talking about the weather, business, etc.)\n3: Friendly/informal conversation (talking about preferences, weekend plans, etc.)\n5: Personal conversation (talking about feelings, personal life, etc.), making them laugh\n6: Compliments, flirty/teasing conversation, doing a favor\n7: Casual intimacy/sex appeal (hand-holding, being unusually close, light skinship, ...)\n8: Date, romance, kissing\n 10: Close physical intimacy, third base and beyond..."
        romanceExample = "Interaction Intimacy Rating 1: 4\n"
  
    instructions = "Do not speak for or otherwise perform actions for the player; your job is to control only the other characters and the surrounding world. Always refer to the player in the second person, as 'you'.\n Before outputting the text to appear in the VN, output the following information, if applicable, formatted exactly: If a character present with the player before the move is no longer present due to leaving, output on its own line Character Leaving: Character X, where X is the number associated to the leaving character. If multiple characters are leaving, use multiple lines. If the character is, say, simply moving to an adjacent room, don't do this; only output Character Leaving if the character is now no longer present in the story. For every character now present in the story (either by still being with the player or by being newly met), output on its own line Character Emotion X: [emotion]. Here X is again the associated character number. [emotion] MUST be one of: neutral-happy, laughing, sad, angry, embarrassed; choose exactly one of these five."+romanceInstructions+" Furthermore, if any of the characters still present have changed clothes from their previous clothes, output again on its own line Character Change Clothes X: [new clothing type]. Here [new clothing type] must be exactly one of: nude, swimsuit, underwear, casual_clothes, work_clothes, exactly as written. Again, it's only necessary to do this if the character is just now changing clothes from what they had on. If the player changes clothes, write on its own line Player Change Clothes: [new clothes]; for the player (unlike other characters), [new clothes] can be any description. Then, finally, again on its own line, write Output: , and then give a brief few-sentence output text for the VN based on what the player has done and what the characters are doing. Include character dialogue if necessary. Any time a character's name and/or dialogue appears, encase it all in <span style=\"color: [hex code];\"></span>, where [hex code] is the color corresponding to that character. Encase BOTH the character's name and their dialogue. Here's an example output, with all data formatted properly; in this scenario, characters 2 and 4 have just left, but characters 1 and 3 are (still) present, and character 3 and the player have just changed into their swimsuits while character 1 hasn't changed clothes: Character Leaving: Character 2\n Character Leaving: Character 4\n Character Emotion 1: laughing\n Character Emotion 3: neutral-happy\n"+romanceExample+" Character Change Clothes 3: swimsuit\n Player Change Clothes: Blue swim trunks\n Output: <span style=\"color: [hex code];\">[Charname]</span> comes up t you. <span style=\"color: [hex code];\">[Charname]: \"Hello!\"</span>... [try to keep this Output under 400 characters]. Note again that everything is on its own line, even the two different Character Leavings, and both character names and dialogue are contained in the color span, and the NPC's change of clothes comes specifically from the list nude, swimsuit, underwear, casual_clothes, work_clothes while the player's change of clothes can be any description. Important: the player CANNOT change locations via this prompt; they must stay in and around the current location. The player also can't advance time via this prompt; the current time is given and fixed."
    promptJSON.append({"role": "system", "content": instructions})
    if len(jailbreak) > 0:
        promptJSON.append({"role": "system", "content": jailbreak})
    if isClaude and len(prefill) > 0:
        promptJSON.append({"role": "assistant", "content": prefill})

    data = {
        "model": model,
        "stream": True,
        "messages": promptJSON
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
    if len(sys.argv) > 5:
        file_path = sys.argv[1]
        with open(file_path, 'r') as f:
            promptJSON = json.load(f)
        model = sys.argv[2]
        jailbreak = sys.argv[3]
        prefill = sys.argv[4]
        boolRomanticProgression = sys.argv[5]
        response_data = gen_text_prompt(promptJSON, model, jailbreak, prefill, boolRomanticProgression)
        print(response_data)



