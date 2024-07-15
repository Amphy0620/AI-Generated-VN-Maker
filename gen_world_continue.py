import requests
import sys
from pathlib import Path
import json
import os

url = os.getenv('proxy_url_gpt')
password = os.getenv('proxy_password')

def gen_world_continue(prompt, output_dir, jailbreak, model, counter):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    headers = {
        "Authorization": f"Bearer {password}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "stream": True,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
            {"role": "system", "content": jailbreak}
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

        with open(output_path / f"world_{counter}.txt", "w") as f:
            f.write(response_content)

if __name__ == "__main__":
    if len(sys.argv) > 9:
        with open(sys.argv[1], 'r') as f:
            prompt = f.read()
        output_dir = sys.argv[2]
        with open(sys.argv[3], 'r') as f:
            jailbreak = f.read()
        numMales = sys.argv[4]
        numFemales = sys.argv[5]
        model = sys.argv[6]
        worldInfo = sys.argv[7]
        with open(sys.argv[8], 'r') as f:
            previousChars = f.read()
        prompt_modified = f"The user wants to create a visual novel with the following scenario: {prompt}. Here's an elaboration on that scenario: {worldInfo}. Continue creating characters to populate the world. These characters should be dictionaries in a JSON array. Their attributes should be \"charNumber\" (an integer which increments with each character), \"charName\" (The full name; unless the user has otherwise specified, default to Japanese names), \"charPersonality\", \"charRelationshipWPlayer\", \"charFaceAndBody\", \"charCasualClothes\", \"charSwimsuit\", \"charWorkClothes\", \"charUnderwear\", and \"charColorCode\". charPersonality should be a 3 to 4 paragraph prose string: The first paragraph should present two or three contrasting but complementary major personality features. For example: charName is prideful and stubborn but unusually horny, or charName is quiet and soft-spoken but can also be very direct. Explain in two or three sentences how these personality features manifest. The second paragraph should present a further two or three minor personality features, for example, charName has an unusually strong sense of smell, or charName is prone to rambling at length about nothing. Explain in another two or three sentences how these additional minor personality features interact with those previously given. Finally, the last one or two paragraphs should be the character's backstory. Briefly tell, starting from childhood and into present day, the character's life story and how they became who they are. Be creative and unique with the personalities! Also, describe potential relationships between characters here, such as charName1 and charName2 are good friends, or sisters, or etc, and also potential relationships with the player. Finally, and very importantly, describe the character's manner of speech and any associated quirks; for example, a rich girl may speak haughtily, hohoho, or a catgirl may intersperse her speech with nya~, or a shy character might... talk very timidly... interesting speech quirks can really sell a character! Consider both positive and negative personality traits; don't be afraid to make a character mean, or angry, or vain, etc. if it's interesting. Have characters fill an interesting diversity of roles that might arise from the setting (unless the player says explicitly what they want). Finally, throughout the whole description, if applicable, elaborate on how the character might react to or interact with the sort of situations that may arise from the suggested scenario, being specific to the user's given prompt. Again, DON'T linebreak. charRelationshipWPlayer MUST be one of: strangers, acquaintances, friends, good friends, sexual tension, lovers, soulmates EXACTLY. Choose exactly one of these 7 options to copy; with no prior information, default to \"acquaintances\". charFaceAndBody should be a string listing booru-style tags that describe the character's looks and physique. For example, \"long hair, red hair, straight hair, blue eyes, medium breasts, ...\". It's especially important to fully describe the hair style/color/length (consider phrases like blunt bangs, parted bangs, ponytail, twintails, hair bun, etc; if the VN is anime-style, feel free to have a diversity of unnatural hair colors), eye color, and breast size. DO NOT describe clothes in charFaceAndBody; imagine you're just seeing them naked. Also include unique bodily features, like \"cat ears, cat tail\" for catgirls, etc. Only include accessories if you can imagine them wearing said accessories while naked; glasses, necklaces, plastic hairbands, wrist scrunchies, etc. are probably fine. Always begin charFaceAndBody with 1boy or 1girl depending on gender. DON'T include the following tags: \"pale skin\", anything muscular for girls. Importantly, if you're describing well-known anime or pop-culture characters, include the full name of the character in charFaceAndBody, for example, \"Hakurei Reimu\", etc. Finally, the last few clothing tags should also be strings of booru-style tags, but ONLY to describe the corresponding clothes (reasonably interpret charWorkClothes as school uniforms, etc. if necessary). For example, charCasualClothes might be \"white t-shirt, denim short shorts, black plastic hairband, ...\". It's important to be as descriptive as possible with these, in particular, ALWAYS include the color of any item. Also inclue bare 'body part' if the outfit doesn't cover it; for example, a bikini would probably have 'bare stomach', or a sleeveless top 'bare arms'. Don't include descriptions of shoes or socks, or anything below the thigh. charColorCode is the hex triplet of a color associated to that character, for example, \"#C0FF00\" for lime green. Make this different for each character; whatever color you choose, make it bright, as it'll be against a dark background. Remember again to repeatedly reinforce the details of the world that the player has provided in descriptions of how characters may interact with the scenario of the prompt. This character creation is a continuation of previous work; here are the characters already generated: {previousChars}. Note that this is in a JSON array, like your output should be, starting with [. As you're creating a continuation of this list, the charNumbers should begin their iteration from where this list ends."
        prompt_modified += f" Continue with exactly {numMales} male characters and {numFemales} female characters in this output."
        counter = sys.argv[9]
        response_data = gen_world_continue(prompt_modified, output_dir, jailbreak, model, counter)