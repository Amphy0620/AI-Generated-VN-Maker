import requests
import sys
from pathlib import Path
import json

url = "https://vip.jewproxy.tech/proxy/aws/claude/v1/messages"  # Replace with your actual URL
password = "68a4f438-9c35-45c1-84d3-a4944d7f484e"  # Replace with your actual password

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

def gen_schedule(prompt, output_dir, char_num, jailbreak, model):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    (output_path / 'charSchedules').mkdir(parents=True, exist_ok=True)

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

        with open(output_path / f"charSchedules/{str(char_num)}_schedule.txt", "w") as f:
            f.write(response_content)

if __name__ == "__main__":
    if len(sys.argv) > 5:
        with open(sys.argv[1], 'r') as f:
            prompt = f.read()
        prompt_modified = f"Given the following visual novel character, world info, and locations: {prompt} \n Construct a detailed schedule for the character, considering where they might go and what they might do at all points of the day. The output should be in the form of a JSON array, where each entry corresponds to a continuous activity. The attributes should be \"startTime\", \"location\", \"activity\", \"clothing\", and \"future_plans\", all strings. startTime should be given in 24 hour format, e.g. 17:30 for 5:30 PM; the activity is assumed to end once the next startTime begins. Feel free to vary startTimes, they can be more realistic than just every half hour. location MUST be one of the listed locationNames. activity is a description of what the character is doing; be moderately descriptive. The activity should be in present tense, e.g. \"sleeping\". clothing MUST come from one of the following set: nude, underwear, casual_clothes, work_clothes, swimsuit. If none seem to fit the activity, just choose the closest one (work_clothes also may include school uniforms, etc.) Do not put ANYTHING other than EXACTLY ONE of the five strings \"nude\", \"underwear\", \"casual_clothes\", \"work_clothes\", \"swimsuit\" here. future_plans should briefly describe anything important (if anything) the character has coming up, as well as the time it begins and whether it's low, medium or high priority; upcoming work or school would be important, leisure time less so. Make the schedules interesting and unique and highly dependent on the character's personality. The schedule will loop, so try to align the ending activity with the start. Include sleeping as an activity (if the character does sleep). Be EXTREMELY thorough in describing the schedule; when does the character eat? Shower? Change methods of study or relaxation? Successive activities in the schedule can still have the same location, like a character might be reading a book in the library for one activity but then doing homework in the library the next. Don't reference other characters when constructing these schedules or explicitly state that other characters are present. Feel free to use smaller increments of time, like 5-15 minutes per activity, in your quest to be thorough. DO NOT use backticks or 'json' to format the output, just give it in pure JSON."
        output_dir = sys.argv[2]
        char_num = sys.argv[3]
        with open(sys.argv[4], 'r') as f:
            jailbreak = f.read()
        model = sys.argv[5]
        response_data = gen_schedule(prompt_modified, output_dir, char_num, jailbreak, model)