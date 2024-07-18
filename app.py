#i coded literally this entire thing in plain notepad LMAO

from flask import Flask, request, jsonify, render_template, url_for
import subprocess
import os
from pathlib import Path
import json
import time
import numpy as np
import random
import cv2
import tempfile

app_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=app_dir)

from basic_functions import get_next_world_folder, minutes_from_time, time_from_minutes, split_char_generations, createAdjacencyMatrix, find_connected_components, add_edge, find_vertex_with_least_connections, find_vertex_with_most_connections, connect_components, find_adjacent_locations, getBackgroundFilePath, get_location_text_description, trimContext

def relationshipDesc(affection, charName):
        if 0 <= affection < 10:
            return charName+" is not acquainted with the player; the two are essentially strangers, and "+charName+"will thus treat the player with the wariness/disinterest/curiosity/etc. that their personality would dictate treating the player. "+charName+" would not do anything with the player they wouldn't do with a total stranger. "+charName+" should immediately rebuff advances by the player."
        if 10 <= affection < 20:
            return "The player is now known to "+charName+" but not acquainted, like coworkers from different projects or classmates who see each other around but don't talk. "+charName+" will still not become too close to the player. "+charName+" should immediately rebuff advances by the player."
        if 20 <= affection < 30:
            return charName+" is now acquainted with the player, like one might be acquinted with a coworker or a classmate from a different friend group. "+charName+" won't mind interacting with the player in a casual context, but still isn't totally comfortable around the player. "+charName+" should immediately rebuff advances by the player, but politely."
        if 30 <= affection < 40:
            return charName+" is becoming more casual with the player. "+charName+" will be more comfortable talking with the player about their personal life, discussing friendly topics, etc. in a casual context. "+charName+" should rebuff advances by the player, but politely."
        if 40 <= affection < 50:
            return charName+" is now properly friendly with the player, and the two can chat, hang out, etc. like you'd expect of casual friends. "+charName+" will still reject advances by the player, but won't be entirely unhappy with them."
        if 50 <= affection < 60:
            return charName+" and the player are now very friendly, and the two can hang out, chat casually even about personal topics, confide in each other, etc. "+charName+" will still reject advances by the player, but won't be entirely unhappy with them."
        if 60 <= affection < 70:
            return "While still very friendly, "+charName+" is now beginning to develop feelings for the player. Not strong enough for them to act on, but they might blush at the player, find themselves thinking about the player, etc. "+charName+" won't accept advances by the player out of confusion, but won't outright reject the player either."
        if 70 <= affection < 80:
            return "In addition to being very friendly, "+charName+" is now outright smitten with the player. "+charName+" will respond positively to the player's advances."
        if 80 <= affection < 90:
            return charName+" is openly smitten with the player, and willing to go all the way with their relationship. However, they're still a bit hesitant about being completely lifetime commital, starting a family, etc. "+charName+" will respond very positively to the player's advances."
        if 90 <= affection < 100:
            return charName+" is openly smitten with the player and committed to furthering their relationship as far as it will go. The player is the love of "+charName+"'s life."
        if affection == 100:
            return charName+" is so deeply in love with the player that they cannot possibly refuse any requests from the player, however crazy or committal. "+charName+"'s whole life revolves around the player."

class Activity:
    def __init__(self, location, activity, clothing, futurePlans):
        self.location = location
        self.activity = activity
        self.clothing = clothing
        self.futurePlans = futurePlans

class Character:
    def __init__(self, num):
        self.num = num
        self.name = None
        self.personality = None
        self.defaultScheduleArray = None
        self.scheduleArray = None
        self.affection = 1
        self.withPlayer = False
        self.clothing = "casual_clothes"
        self.emotion = "neutral-happy"
        self.clothingDescription = {"charFaceAndBody": "", "casual_clothes": "", "swimsuit": "", "work_clothes": "", "underwear": "", "nude": ""}
        self.color = None
    def currentActivity(self, currentTimeMins):
        for i in range(len(self.scheduleArray)):
            current_activity = self.scheduleArray[i]
            next_activity = self.scheduleArray[(i + 1) % len(self.scheduleArray)]
            start_time = minutes_from_time(current_activity['startTime'])
            end_time = minutes_from_time(next_activity['startTime'])
            if end_time <= start_time:
                end_time += 1440
            if start_time <= currentTimeMins < end_time or (start_time <= currentTimeMins + 1440 < end_time):
                return Activity(
                    location=current_activity['location'],
                    activity=current_activity['activity'],
                    clothing=current_activity['clothing'],
                    futurePlans=current_activity['future_plans']
                )

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Submit Prompt</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            h1 {
                font-size: 24px;
                font-weight: normal;
                text-align: center;
                margin-bottom: 20px;
            }
            #promptForm {
                display: flex;
                flex-direction: column;
                max-width: 1000px;
                margin: 0 auto;
            }
            .form-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            .form-block {
                flex: 1;
                display: flex;
                flex-direction: column;
                margin-right: 20px;
            }
            .form-block:last-child {
                margin-right: 0;
            }
            .form-group {
                display: flex;
                flex-direction: column;
                margin-bottom: 10px;
            }
            .form-group input, .form-group textarea {
                font-size: 16px;
                padding: 10px;
                margin-bottom: 5px;
            }
            .form-group textarea {
                height: 50px;
                overflow-y: auto;
            }
            .form-group .large-textarea {
                height: 100px;
            }
            .small-input {
                width: 100px;
            }
            .form-group-inline {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .form-group-inline .form-group {
                flex: 1;
                margin-right: 10px;
            }
            .form-group-inline .form-group:last-child {
                margin-right: 0;
            }
            .small-text {
                font-size: 12px;
                font-style: italic;
                margin-bottom: 5px;
            }
            button {
                font-size: 16px;
                padding: 10px;
                margin-top: 10px;
            }
            #playerDescription {
                height: 120px;
            }
            .form-group-checkbox {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            .form-group-checkbox label {
                margin-right: 10px;
                white-space: nowrap;
            }
            .form-group-checkbox input {
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <h1>AI-Generated Visual Novel Maker!</h1>
        <form id="promptForm">
            <div class="form-row">
                <div class="form-block">
                    <div class="form-group">
                        <label for="playerName">Your name:</label>
                        <textarea id="playerName" name="playerName" placeholder="Name your character"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="playerDescription">Your description:</label>
                        <textarea id="playerDescription" name="playerDescription" placeholder="(Optional) Describe your character"></textarea>
                    </div>
                </div>
                <div class="form-block">
                    <div class="form-group-inline">
                        <div class="form-group">
                            <label for="proxyUrl">Endpoint URL:</label>
                            <textarea id="proxyUrl" name="proxyUrl" placeholder="Should end with /v1"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="proxyPassword">API Key/Proxy password:</label>
                            <textarea id="proxyPassword" name="proxyPassword"></textarea>
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="small-text">
                            Strong suggestion: Use 4o and detailed premade character descriptions for recreating established worlds/characters, or use Sonnet 3.5 or Opus for creating original stuff. Don't actually use any models other than those three.
                        </div>
                        <label for="model">Model:</label>
                        <select id="model" name="model">
                            <option value="gpt-4o">gpt-4o</option>
                            <option value="gpt-4o-2024-05-13">gpt-4o-2024-05-13</option>
                            <option value="gpt-4-turbo">gpt-4-turbo</option>
                            <option value="gpt-4-turbo-2024-04-09">gpt-4-turbo-2024-04-09</option>
                            <option value="gpt-4-turbo-preview">gpt-4-turbo-preview</option>
                            <option value="gpt-4-0125-preview">gpt-4-0125-preview</option>
                            <option value="gpt-4-1106-preview">gpt-4-1106-preview</option>
                            <option value="gpt-4">gpt-4</option>
                            <option value="gpt-4-0613">gpt-4-0613</option>
                            <option value="gpt-4-0314">gpt-4-0314</option>
                            <option value="claude-3-5-sonnet-20240620">claude-3-5-sonnet-20240620</option>
                            <option value="claude-3-opus-20240229">claude-3-opus-20240229</option>
                            <option value="claude-3-sonnet-20240229">claude-3-sonnet-20240229</option>
                        </select>
                    </div>
                    <div class="form-group-inline">
                        <div class="form-group">
                            <label for="naiUsername">NAI username:</label>
                            <textarea id="naiUsername" name="naiUsername"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="naiPassword">NAI password:</label>
                            <textarea id="naiPassword" name="naiPassword"></textarea>
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-row">
                <div class="form-block">
                    <div class="form-group">
                        <label for="worldGenJailbreak">World/Character generation jailbreak:</label>
                        <textarea id="worldGenJailbreak" name="worldGenJailbreak" placeholder="(Optional) Highly influences the generation of world info and characters."></textarea>
                    </div>
                    <div class="form-group">
                        <label for="locationGenJailbreak">Location generation jailbreak:</label>
                        <textarea id="locationGenJailbreak" name="locationGenJailbreak" placeholder="(Optional) Highly influences the generation of the different locations. (Suggestion: Impose a certain number of locations here. 45-ish is a soft limit due to token output restrictions. Without a specific number, the AI seems to like to make 20 or so.)"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="scheduleGenJailbreak">Schedule generation jailbreak:</label>
                        <textarea id="scheduleGenJailbreak" name="scheduleGenJailbreak" placeholder="(Optional) Highly influences the generation of the characters' schedules and what they do."></textarea>
                    </div>
                </div>
                <div class="form-block">
                    <div class="form-group">
                        <label for="charVisualStyle">Character visual style:</label>
                        <textarea id="charVisualStyle" name="charVisualStyle" placeholder="(Optional, but recommended) Specific style prompts help make character images look more consistent with each other. They get added to all the character-based NAI image gen prompts (and so work best with booru tags). Examples: 1980s (style), Monogatari, anime screencap, ..."></textarea>
                    </div>
                    <div class="small-text">
                        Each character adds ~8-9 mins to the total gen time. Default values are 0 boys and 3 girls.
                    </div>
                    <div class="form-group-inline">
                        <div class="form-group">
                            <label for="numMaleChars"># of male characters:</label>
                            <input type="number" id="numMaleChars" name="numMaleChars" class="small-input">
                        </div>
                        <div class="form-group">
                            <label for="numFemaleChars"># of female characters:</label>
                            <input type="number" id="numFemaleChars" name="numFemaleChars" class="small-input">
                        </div>
                    </div>
                    <div class="small-text">
                        This doesn't use a tokenizer, so we just count characters. Estimate 1 token~4 characters.
                    </div>
                    <div class="form-group-inline">
                        <div class="form-group">
                            <label for="maxContextSize">Max. context size (in characters):</label>
                            <input type="number" id="maxContextSize" name="maxContextSize" class="small-input">
                        </div>
                        <div class="form-group">
                            <label for="maxProxyGensPerMin">Max. text gens per minute:</label>
                            <input type="number" id="maxProxyGensPerMin" name="maxProxyGensPerMin" class="small-input">
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-group-checkbox">
                <label for="romanceCheckbox">Stat-based Romance Progression?</label>
                <input type="checkbox" id="romanceCheckbox" name="romanceCheckbox">
                <div class="small-text">If checked, all characters will have a hidden affection stat which can be raised with positive interactions and which dictates their relationship with you.</div>
            </div>
            <div class="form-group-inline">
                <label for="worldName">World Name:</label>
                <textarea id="worldName" name="worldName" class="small-input"></textarea>
                <div class="small-text">Name your VN; don't use special characters that can't appear in a file name. DON'T change this in the middle of the generation process.
</div>
            </div>
            <div class="form-group">
                <label for="prompt">Your prompt:</label>
                <textarea id="prompt" name="prompt" class="large-textarea" placeholder="Describe the VN you want to generate here. The more detailed you are the better; don't assume the AI has any creativity of its own. (Suggestion: Give pre-made character descriptions, let 4o do the initial generation, and then use Claude to actually play the VN. Example dialogue helps a lot as well; say to reproduce it exactly in the character descriptions.)"></textarea>
            </div>
                <button type="submit" name="action" value="gen_world">(Step 1) Generate World Info and Characters</button>
                <div id="gen_world_output" class="small-text"></div>
                <button type="submit" name="action" value="gen_loc">(Step 2) Generate Locations</button>
                <div id="gen_loc_output" class="small-text"></div>
                <button type="submit" name="action" value="gen_sched">(Step 3) Generate Character Schedules</button>
                <div id="gen_sched_output" class="small-text"></div>
                <button type="submit" name="action" value="init">(Step 4) Generate Images and Initialize</button>
                <button type="button" id="loadSaveBtn">Load Old Save</button>
                <input type="file" id="fileInput" style="display: none;" />
        </form>
        <script>
                document.getElementById('promptForm').addEventListener('submit', async function(event) {
                        event.preventDefault();

                        const formData = {
                                prompt: document.getElementById('prompt').value,
                                playerName: document.getElementById('playerName').value,
                                playerDescription: document.getElementById('playerDescription').value,
                                proxyUrl: document.getElementById('proxyUrl').value,
                                proxyPassword: document.getElementById('proxyPassword').value,
                                naiUsername: document.getElementById('naiUsername').value,
                                naiPassword: document.getElementById('naiPassword').value,
                                model: document.getElementById('model').value,
                                worldGenJailbreak: document.getElementById('worldGenJailbreak').value,
                                locationGenJailbreak: document.getElementById('locationGenJailbreak').value,
                                scheduleGenJailbreak: document.getElementById('scheduleGenJailbreak').value,
                                charVisualStyle: document.getElementById('charVisualStyle').value,
                                numMaleChars: document.getElementById('numMaleChars').value,
                                numFemaleChars: document.getElementById('numFemaleChars').value,
                                maxContextSize: document.getElementById('maxContextSize').value,
                                maxProxyGensPerMin: document.getElementById('maxProxyGensPerMin').value,
                                romanceCheckbox: document.getElementById('romanceCheckbox').checked,
                                worldName: document.getElementById('worldName').value
                        };

                        const action = event.submitter.value;

                        let url = '';
                        switch (action) {
                                case 'gen_world':
                                        url = '/gen_world';
                                        break;
                                case 'gen_loc':
                                        url = '/gen_loc';
                                        break;
                                case 'gen_sched':
                                        url = '/gen_sched';
                                        break;
                                case 'init':
                                        url = '/init';
                                        break;
                        }

                        const response = await fetch(url, {
                                method: 'POST',
                                headers: {
                                        'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(formData),
                        });

                        const result = await response.json();
                        switch (url) {
                                case '/gen_world':
                                        document.getElementById('gen_world_output').innerHTML = "World and character data successfully generated and saved to "+result.world_file_path+".<br>Check and edit the generation if you like, then move on to Step 2.";
                                        document.getElementById('worldName').innerHTML = result.folderName;
                                        break;
                                case '/gen_loc':
                                        document.getElementById('gen_loc_output').innerHTML = "Location data successfully generated and saved to "+result.loc_file_path+".<br>Check and edit the generation if you like, then move on to Step 3. (Note: We do a little adjacency post-processing to make sure the map is connected and movement is bidirectional.)";
                                        break;
                                case '/gen_sched':
                                        document.getElementById('gen_sched_output').innerHTML = "Schedule data successfully generated and saved in "+result.sched_file_path+".<br>Check and edit the generations if you like, then move on to Step 4.";
                                        break;
                                case '/init':
                                        document.documentElement.innerHTML = result.new_html;
                                        break;
                        }
                });

                document.getElementById('loadSaveBtn').addEventListener('click', function() {
                        document.getElementById('fileInput').click();
                });

            document.getElementById('fileInput').addEventListener('change', async function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = async function(e) {
                        const fileContent = e.target.result;
                        try {
                            const jsonContent = JSON.parse(fileContent);
                            const response = await fetch('/load', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(jsonContent),
                            });
                            const result = await response.json();
                            document.documentElement.innerHTML = result.new_html;
                        } catch (error) {
                            console.error("Failed to parse JSON file content:", error);
                        }
                    };
                    reader.readAsText(file);
                }
            });
        </script>
    </body>
    </html>
    '''

playerName = ""
playerDescription = ""
promptOpener = ""
output_dir = None
currentLocation = ""
currentAdjacentLocations = []
currentClothing = ""
currentTime = ""
charArrayDict = []
charArrayObj = []
charArrayWithPlayerNums = []
locationArray = []
allLocationsStr = ""
adjacencyMatrix = [[]]
storySoFar = []
worldInfo = ""
maxContextChars = 120000
maxGensPerMinute = 3
currentOutput = ""
boolRomanticProgression = False
model = None

def refreshValues():
    global playerName, playerDescription, output_dir, currentLocation, currentAdjacentLocations, currentClothing, currentTime, charArrayDict, charArrayWithPlayerNums, locationArray, allLocationsStr, adjacencyMatrix, storySoFar, worldInfo, maxContextChars, currentOutput, charArrayObj, boolRomanticProgression
    playerName = ""
    playerDescription = ""
    promptOpener = ""
    output_dir = None
    currentLocation = ""
    currentAdjacentLocations = []
    currentClothing = ""
    currentTime = ""
    charArrayDict = []
    charArrayObj = []
    charArrayWithPlayerNums = []
    locationArray = []
    allLocationsStr = ""
    adjacencyMatrix = [[]]
    storySoFar = []
    worldInfo = ""
    maxContextChars = 120000
    maxGensPerMinute = 3
    currentOutput = ""
    boolRomanticProgression = False    

@app.route('/gen_world', methods=['POST'])
def gen_world():
    data = request.json
    refreshValues()
    global output_dir

    folderName = ""
    VN_name = data['worldName']
    base_dir = Path("generated_VNs")
    base_dir.mkdir(parents=True, exist_ok=True)
    if len(VN_name) > 0:
        output_dir = base_dir / VN_name
        output_dir.mkdir(exist_ok=True)
    else:
        output_dir = get_next_world_folder()
        folderName = output_dir.as_posix().rsplit('/', 1)[-1]
        output_dir.mkdir(exist_ok=True)

    global playerName, playerDescription, promptOpener, storySoFar, worldInfo, maxContextChars, maxGensPerMinute, allLocationsStr, boolRomanticProgression

    maxGensPerMinute = 3
    if len(data['maxProxyGensPerMin']) > 0:
        maxGensPerMinute = int(data['maxProxyGensPerMin'])
    sleepTime = 60 // maxGensPerMinute + 2

    data = request.json
    prompt = data['prompt']
    playerName = data['playerName']
    if len(playerName) == 0:
        playerName = "Ballsack"
    playerDescription = data['playerDescription']
    promptOpener = f"The player's name is {playerName}. A description of the player: {playerDescription}"

    prompt_modified = prompt+"\n Player information: "+promptOpener

    worldJB = data['worldGenJailbreak']

    numMalesStr = data['numMaleChars']
    numFemalesStr = data['numFemaleChars']

    proxyURL = data['proxyUrl']
    proxyPassword = data['proxyPassword']
    NAIUsername = data['naiUsername']
    NAIPassword = data['naiPassword']

    os.environ['proxy_url'] = proxyURL
    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword
    if len(NAIUsername) > 0:
        os.environ['NAI_USERNAME'] = NAIUsername
    if len(NAIPassword) > 0:
        os.environ['NAI_PASSWORD'] = NAIPassword

    maxChars = data['maxContextSize']
    if len(maxChars) > 0:
        maxContextChars = maxChars

    if len(numMalesStr) == 0:
        numMalesStr = "0"
    if len(numFemalesStr) == 0:
        numFemalesStr = "3"

    model = data['model']

    numMalesInt = int(numMalesStr)
    numFemalesInt = int(numFemalesStr)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_prompt:
        temp_file_prompt.write(prompt_modified)
        temp_file_prompt_path = temp_file_prompt.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_worldJB:
        temp_file_worldJB.write(worldJB)
        temp_file_worldJB_path = temp_file_worldJB.name

    totalCharGens = split_char_generations(numMalesInt, numFemalesInt)

    global charArrayDict, worldInfo
    charArrayDict = []

    try:
        result1 = subprocess.run(['python', 'gen_world.py', temp_file_prompt_path, str(output_dir), temp_file_worldJB_path, str(totalCharGens[0][0]), str(totalCharGens[0][1]), model], capture_output=True, text=True)

        char_file = output_dir / "world_0.txt"
        wait_time = 0
        max_wait_time = 300  # Maximum wait time of 30 seconds
        while wait_time < max_wait_time:
            if char_file.exists() and char_file.stat().st_size > 0:
                break
            time.sleep(1)
            wait_time += 1
        if wait_time >= max_wait_time:
            return jsonify(message='Timeout waiting for world.txt to be generated.'), 500

        with open(char_file, 'r') as f:
            chars = json.load(f)

        worldInfo = chars.get('world_info')
        charArrayDict = chars.get('chars')

        os.remove(char_file)

        counter = 2
        while counter <= len(totalCharGens):
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_charsSoFar:
                temp_file_charsSoFar.write(json.dumps(charArrayDict))
                temp_file_charsSoFar_path = temp_file_charsSoFar.name
    
            time.sleep(sleepTime)
            try:             
                result1 = subprocess.run(['python', 'gen_world_continue.py', temp_file_prompt_path, str(output_dir), temp_file_worldJB_path, str(totalCharGens[counter - 1][0]), str(totalCharGens[counter - 1][1]), model, worldInfo, temp_file_charsSoFar_path, str(counter)], capture_output=True, text=True)

                char_file_new = output_dir / f"world_{counter}.txt"
                wait_time = 0
                max_wait_time = 300  # Maximum wait time of 30 seconds
                while wait_time < max_wait_time:
                    if char_file_new.exists() and char_file_new.stat().st_size > 0:
                        break
                    time.sleep(1)
                    wait_time += 1
                if wait_time >= max_wait_time:
                    return jsonify(message='Timeout waiting for world.txt to be generated.'), 500

                newChars = []  
                with open(char_file_new, 'r') as f:
                    newChars = json.load(f)

                charArrayDict += newChars
                counter += 1
                os.remove(char_file_new)

            finally:
                os.remove(temp_file_charsSoFar_path)

    finally:
        os.remove(temp_file_prompt_path)
        os.remove(temp_file_worldJB_path) 

    worldFull = {}
    worldFull['world_info'] = worldInfo
    worldFull['chars'] = charArrayDict

    path_to_world = output_dir / "world_and_chars.txt"
    with open(path_to_world, "w") as f:
        json.dump(worldFull, f, indent=4)

    return jsonify({'world_file_path': path_to_world.as_posix(), 'folderName': folderName})



@app.route('/gen_loc', methods=['POST'])
def gen_loc():
    data = request.json
    refreshValues()
    global output_dir

    VN_name = data['worldName']
    base_dir = Path("generated_VNs")
    base_dir.mkdir(parents=True, exist_ok=True)
    output_dir = base_dir / VN_name
    output_dir.mkdir(exist_ok=True)

    global playerName, playerDescription, promptOpener, storySoFar, worldInfo, maxContextChars, maxGensPerMinute, allLocationsStr, boolRomanticProgression
 
    maxGensPerMinute = 3
    if len(data['maxProxyGensPerMin']) > 0:
        maxGensPerMinute = int(data['maxProxyGensPerMin'])
    sleepTime = 60 // maxGensPerMinute + 2

    data = request.json
    locJB = data['locationGenJailbreak']

    proxyURL = data['proxyUrl']
    proxyPassword = data['proxyPassword']
    NAIUsername = data['naiUsername']
    NAIPassword = data['naiPassword']

    os.environ['proxy_url'] = proxyURL
    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword
    if len(NAIUsername) > 0:
        os.environ['NAI_USERNAME'] = NAIUsername
    if len(NAIPassword) > 0:
        os.environ['NAI_PASSWORD'] = NAIPassword

    model = data['model']

    char_file = output_dir / "world_and_chars.txt"

    with open(char_file, 'r') as f:
        worldContentStr = f.read()

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_worldContent:
        temp_file_worldContent.write(worldContentStr)
        temp_file_worldContent_path = temp_file_worldContent.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_locJB:
        temp_file_locJB.write(locJB)
        temp_file_locJB_path = temp_file_locJB.name

    time.sleep(sleepTime)
    try:
        result2 = subprocess.run(['python', 'gen_locations.py', temp_file_worldContent_path, str(output_dir), temp_file_locJB_path, model], capture_output=True, text=True)

    finally:
        os.remove(temp_file_worldContent_path)
        os.remove(temp_file_locJB_path)

    path_to_loc = output_dir / "locations.txt"

    return jsonify({'loc_file_path': path_to_loc.as_posix()})



@app.route('/gen_sched', methods=['POST'])
def gen_sched():

    data = request.json
    refreshValues()
    global output_dir

    VN_name = data['worldName']
    base_dir = Path("generated_VNs")
    base_dir.mkdir(parents=True, exist_ok=True)
    output_dir = base_dir / VN_name
    output_dir.mkdir(exist_ok=True)

    global playerName, playerDescription, promptOpener, storySoFar, worldInfo, maxContextChars, maxGensPerMinute, allLocationsStr, boolRomanticProgression

    maxGensPerMinute = 3
    if len(data['maxProxyGensPerMin']) > 0:
        maxGensPerMinute = int(data['maxProxyGensPerMin'])
    sleepTime = 60 // maxGensPerMinute + 2

    data = request.json
    schedJB = data['scheduleGenJailbreak']

    proxyURL = data['proxyUrl']
    proxyPassword = data['proxyPassword']
    NAIUsername = data['naiUsername']
    NAIPassword = data['naiPassword']

    os.environ['proxy_url'] = proxyURL
    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword
    if len(NAIUsername) > 0:
        os.environ['NAI_USERNAME'] = NAIUsername
    if len(NAIPassword) > 0:
        os.environ['NAI_PASSWORD'] = NAIPassword

    model = data['model']




    world_file = output_dir / "world_and_chars.txt"
    location_file = output_dir / "locations.txt"

    with open(location_file, 'r') as f:
        locationsStr = f.read()
    with open(world_file, 'r') as f:
        chars = json.load(f)

    charArrayDict = chars['chars']

    for char in charArrayDict:
        infoForSchedule = "Character Name: "+char['charName']+" Character Info: "+char['charPersonality']+" World Info: "+chars['world_info']+" Locations: "+locationsStr

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_schedInfo:
            temp_file_schedInfo.write(infoForSchedule)
            temp_file_schedInfo_path = temp_file_schedInfo.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file_schedJB:
            temp_file_schedJB.write(schedJB)
            temp_file_schedJB_path = temp_file_schedJB.name

        try:
            subprocess.run(['python', 'gen_schedule.py', temp_file_schedInfo_path, str(output_dir), str(char['charNumber']), temp_file_schedJB_path, model], capture_output=True, text=True)
        
        finally:
            os.remove(temp_file_schedInfo_path)
            os.remove(temp_file_schedJB_path)

        time.sleep(sleepTime)

    path_to_sched = output_dir / "charSchedules"

    return jsonify({'sched_file_path': path_to_sched.as_posix()})




@app.route('/init', methods=['POST'])
def init():
    data = request.json
    refreshValues()
    global output_dir

    VN_name = data['worldName']
    base_dir = Path("generated_VNs")
    base_dir.mkdir(parents=True, exist_ok=True)
    output_dir = base_dir / VN_name
    output_dir.mkdir(exist_ok=True)

    global playerName, playerDescription, promptOpener, storySoFar, worldInfo, maxContextChars, maxGensPerMinute, allLocationsStr, boolRomanticProgression

    maxGensPerMinute = 3
    if len(data['maxProxyGensPerMin']) > 0:
        maxGensPerMinute = int(data['maxProxyGensPerMin'])
    sleepTime = 60 // maxGensPerMinute + 2

    playerName = data['playerName']
    if len(playerName) == 0:
        playerName = "Ballsack"
    playerDescription = data['playerDescription']
    promptOpener = f"The player's name is {playerName}. A description of the player: {playerDescription}"

    proxyURL = data['proxyUrl']
    proxyPassword = data['proxyPassword']
    NAIUsername = data['naiUsername']
    NAIPassword = data['naiPassword']

    os.environ['proxy_url'] = proxyURL
    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword
    if len(NAIUsername) > 0:
        os.environ['NAI_USERNAME'] = NAIUsername
    if len(NAIPassword) > 0:
        os.environ['NAI_PASSWORD'] = NAIPassword

    maxChars = data['maxContextSize']
    if len(maxChars) > 0:
        maxContextChars = maxChars

    style = data['charVisualStyle']
    model = data['model']
    boolRomanticProgression = data['romanceCheckbox']

    world_file = output_dir / "world_and_chars.txt"
    location_file = output_dir / "locations.txt"

    global locationArray, adjacencyMatrix

    with open(location_file, 'r') as f:
        locations = json.load(f)

    locationArray = locations
    isHubArea = []
    for location in locationArray:
        allLocationsStr += location['locationName']+", "
        isHubArea.append(location['isHubArea'])
    adjacencyMatrix = createAdjacencyMatrix(locationArray)
    
    while adjacencyMatrix != connect_components(adjacencyMatrix, isHubArea):
        adjacencyMatrix = connect_components(adjacencyMatrix, isHubArea)

    with open(location_file, 'r') as f:
        locationsStr = f.read()
    with open(world_file, 'r') as f:
        chars = json.load(f)

    global worldInfo, charArrayDict, charArrayObj
    worldInfo = chars['world_info']
    charArrayDict = chars['chars']

    for char in charArrayDict:
        i = char.get('charNumber')
        character = Character(i)
        character.name = char.get('charName')
        character.personality = char.get('charPersonality')
        character.color = char.get('charColorCode')
        character.clothingDescription['charFaceAndBody'] = char.get('charFaceAndBody')
        character.clothingDescription['underwear'] = char.get('charUnderwear')
        character.clothingDescription['swimsuit'] = char.get('charSwimsuit')
        character.clothingDescription['work_clothes'] = char.get('charWorkClothes')
        character.clothingDescription['casual_clothes'] = char.get('charCasualClothes')

        if char.get('charRelationshipWPlayer') == "acquaintances":
            character.affection = 20
        if char.get('charRelationshipWPlayer') == "friends":
            character.affection = 40
        if char.get('charRelationshipWPlayer') == "good friends":
            character.affection = 50
        if char.get('charRelationshipWPlayer') == "sexual tension":
            character.affection = 60
        if char.get('charRelationshipWPlayer') == "lovers":
            character.affection = 80
        if char.get('charRelationshipWPlayer') == "soulmates":
            character.affection = 100
        charArrayObj.append(character)

    for char in charArrayObj:
        schedule_file = output_dir / "charSchedules" / f"{char.num}_schedule.txt"

        with open(schedule_file, 'r') as f:
            schedule = json.load(f)
        char.scheduleArray = schedule
        char.defaultScheduleArray = char.scheduleArray

    emotions = [{"name": "neutral-happy", "description": "light smile"}, {"name": "laughing", "description": "laughing, open mouth"}, {"name": "sad", "description": "sad, frown"}, {"name": "angry", "description": "angry, fury"}, {"name": "embarrassed", "description": "embarrassed, blush, full-face blush"}]

    for char in charArrayDict:
        fixedSeed = random.randint(1, 2**32 - 1)
        clothingStyles = [{"name": "nude", "description": "{{nsfw, completely nude, uncensored}}"}, {"name": "casual_clothes", "description": char['charCasualClothes']}, {"name": "work_clothes", "description": char['charWorkClothes']}, {"name": "swimsuit", "description": char['charSwimsuit']}, {"name": "underwear", "description": char['charUnderwear']}] 
        for emotion in emotions:
            for clothes in clothingStyles:
                subprocess.run(['python', 'generate_image_simplified.py', "{{{solo, white background, cowboy shot, straight-on, looking at viewer}}}, "+char['charFaceAndBody']+", "+clothes['description']+", "+emotion['description']+", "+style, str(output_dir)+"/charImages", "char_"+str(char['charNumber'])+"_"+clothes['name']+"_"+emotion['name'], 'True', str(fixedSeed)], capture_output=True, text=True)
                subprocess.run(['python', 'trimWhite.py', str(output_dir)+"/charImages/char_"+str(char['charNumber'])+"_"+clothes['name']+"_"+emotion['name']+".png"], capture_output=True, text=True)

    for location in locations:
        if location['isOutdoors']:
            fixedSeed = random.randint(1, 2**32 - 1)
            subprocess.run(['python', 'generate_image_simplified.py', "{{{scenery, no humans, outdoors}}}, [[[[[day]]]]], "+location['locationName']+" "+location['locationTagDescription'], str(output_dir)+"/locationImages", "location_"+str(location['locationNumber'])+"_day", 'False', str(fixedSeed)], capture_output=True, text=True)
            subprocess.run(['python', 'generate_image_simplified.py', "{{{scenery, no humans, outdoors}}}, [[[[[night]]]]], "+location['locationName']+" "+location['locationTagDescription'], str(output_dir)+"/locationImages", "location_"+str(location['locationNumber'])+"_night", 'False', str(fixedSeed)], capture_output=True, text=True)   
        else:
            subprocess.run(['python', 'generate_image_simplified.py', "{{{scenery, no humans, indoors}}}, [[[[[day]]]]], "+location['locationName']+" "+location['locationTagDescription'], str(output_dir)+"/locationImages", "location_"+str(location['locationNumber'])+"_day", 'False', str(fixedSeed)], capture_output=True, text=True)
            subprocess.run(['python', 'generate_image_simplified.py', "{{{scenery, no humans, indoors}}}, [[[[[night]]]]], "+location['locationName']+" "+location['locationTagDescription'], str(output_dir)+"/locationImages", "location_"+str(location['locationNumber'])+"_night", 'False', str(fixedSeed)], capture_output=True, text=True)   

    firstOutput = None
    time.sleep(sleepTime)

    firstOutput = subprocess.run(['python', 'initialize.py', promptOpener, chars['world_info']+" "+locationsStr, model], capture_output=True, text=True)

    global currentLocation, currentAdjacentLocations, currentTime, currentClothing, backgroundFile, currentOutput

    currentLocation = firstOutput.stdout.split("New location:")[1].split("\n")[0].strip()
    currentTime = firstOutput.stdout.split("Current time:")[1].split("\n")[0].strip()
    currentClothing = firstOutput.stdout.split("Current clothes:")[1].split("\n")[0].strip()
    textOutput = firstOutput.stdout.split("Output:")[1].strip()
    currentLocationDict = next((loc for loc in locationArray if loc['locationName'] == currentLocation), None)
    backgroundFile = getBackgroundFilePath(output_dir, currentLocationDict, minutes_from_time(currentTime))
    currentAdjacentLocations = find_adjacent_locations(locationArray, currentLocation, adjacencyMatrix)

    storySoFar.append({"role": "assistant", "content": textOutput})
    currentOutput = textOutput

    save()
    return render_game_interface(textOutput, "")

@app.route('/move_to', methods=['POST'])
def move_to():
    data = request.get_json()
    location = data.get('location')
    jailbreak = data.get('jailbreak')
    proxyURL = data.get('proxyURL')
    proxyPassword = data.get('proxyPassword')
    prefill = data.get('prefill')
    model = data.get('model')
    maxChars = data.get('maxChars')
    prompt = data.get('prompt')

    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword

    global currentLocation, currentAdjacentLocations, currentTime, currentClothing, backgroundFile, currentTime, charArrayObj, charArrayWithPlayerNums, storySoFar, promptOpener, maxContextChars, currentOutput
    textOutput = ""
   
    if len(maxChars) > 0:
        maxContextChars = maxChars

    currentTime = time_from_minutes(minutes_from_time(currentTime) + 3)
    previousLocation = currentLocation
    currentLocation = location
    currentLocationDict = next((loc for loc in locationArray if loc['locationName'] == currentLocation), None)
    backgroundFile = getBackgroundFilePath(output_dir, currentLocationDict, minutes_from_time(currentTime))
    backgroundFileStr = str(url_for('static', filename=backgroundFile + '.png'))
    currentAdjacentLocations = find_adjacent_locations(locationArray, currentLocation, adjacencyMatrix)

    charsAlreadyWithPlayer = []
    charsNewlyMet = []

    for char in charArrayObj:
        if char.withPlayer:
            charsAlreadyWithPlayer.append(char)
        if not char.withPlayer:
            char.emotion = "neutral-happy"
            char.clothing = char.currentActivity(minutes_from_time(currentTime)).clothing
        if char.currentActivity(minutes_from_time(currentTime)).location == currentLocation and not char.withPlayer:
            char.withPlayer = True
            charsNewlyMet.append(char)

    charArrayWithPlayerFileLocations = []
    charArrayWithPlayerNums = []

    if len(charsAlreadyWithPlayer)+len(charsNewlyMet) == 0:
        textOutput = "You move to "+currentLocation+"."
        if len(prompt) > 0:
            storySoFar.append({"role": "user", "content": prompt})
        storySoFar.append({"role": "system", "content": playerName+" moves to "+currentLocation+". Nobody else is present."})

    else:
        newContent = playerName+" moves from "+previousLocation+" to "+currentLocation+". "
        if len(charsNewlyMet) > 0:
            newContent += "The following new characters are present at that location. "
            for char in charsNewlyMet:
                newContent+=char.name+" (character number "+str(char.num)+") is performing the activity: "+char.currentActivity(minutes_from_time(currentTime)).activity+". Their current clothing is "+char.currentActivity(minutes_from_time(currentTime)).clothing+" ("+char.clothingDescription[char.currentActivity(minutes_from_time(currentTime)).clothing]+"). Their immediate plans are "+char.currentActivity(minutes_from_time(currentTime)).futurePlans+".\n"
        else:
            newContent+= "No characters are present at the new location."
        if len(charsAlreadyWithPlayer) > 0:
            newContent += "The following characters were present with "+playerName+" at the previous location. They may or may not still be present in the story."
            for char in charsAlreadyWithPlayer:
                newContent += char.name+" (character number: "+str(char.num)+"). Their current clothing is "+char.clothing+" ("+char.clothingDescription[char.clothing]+"). Their immediate plans (if not already broken) are "+char.currentActivity(minutes_from_time(currentTime)).futurePlans+".\n"

        charDescriptions = "Relevant character descriptions: "
        for char in charsAlreadyWithPlayer + charsNewlyMet:
            charDescriptions += char.name+" (character number "+str(char.num)+", character color code: "+char.color+"): "+char.personality+" Appearance: "+char.clothingDescription['charFaceAndBody']+"\n"
            if boolRomanticProgression:
                charDescriptions += char.name+"'s relationship with the player has updated based on previous interactions: "+relationshipDesc(char.affection, char.name)+"\n"

        if len(prompt) > 0:
            storySoFar.append({"role": "user", "content": prompt})

        newContent = newContent.strip()

        fixedContext = 0
        opener = "You are the narrator for a visual novel being played by the player, "+playerName+". Output what happens next along with any character dialogue and other requested information, correctly formatted."
        worldStuff = "Information about the world: "+worldInfo
        locationStuff = "The following are all the accessible locations in this world; any location you refer to must come from this list exactly: "+allLocationsStr
        playerStuff = "Information about the player: "+promptOpener+" The current time (in 24 hour format) is "+currentTime+", the player's current location is "+currentLocation+"("+get_location_text_description(locationArray, currentLocation)+") and the player's current clothing is "+currentClothing+"."
        instructionsLength = 3772

        fixedContext += len(opener)+len(worldStuff)+len(locationStuff)+len(playerStuff)+len(charDescriptions)+len(newContent)+len(jailbreak)+instructionsLength
        if model[:6] == "claude":
            fixedContext += len(prefill) + 85

        contextLeft = int(maxContextChars) - fixedContext
        storySoFar = trimContext(contextLeft, storySoFar)

        sendToAIJSON = [{"role": "system", "content": opener}]
        sendToAIJSON.append({"role": "system", "content": worldStuff})
        sendToAIJSON.append({"role": "system", "content": locationStuff})
        sendToAIJSON.append({"role": "system", "content": playerStuff})
        sendToAIJSON.append({"role": "system", "content": charDescriptions})
        sendToAIJSON += storySoFar
        sendToAIJSON.append({"role": "system", "content": newContent})

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            json.dump(sendToAIJSON, temp_file)
            temp_file_path = temp_file.name

        AIresponse = None
        try:
            AIresponse = subprocess.run(['python', 'gen_text_button.py', temp_file_path, model, jailbreak, prefill, str(boolRomanticProgression)], capture_output=True, text=True)
        finally:
            os.remove(temp_file_path)            
        rawOutput = AIresponse.stdout
        textOutput = rawOutput.split("Output:")[1].strip()
        storySoFar.append({"role": "system", "content": playerName+" moves to "+currentLocation+"."})
        storySoFar.append({"role": "assistant", "content": textOutput})

        clothingStyles = ["nude", "underwear", "swimsuit", "casual_clothes", "work_clothes"]
        emotions = ["neutral-happy", "laughing", "sad", "angry", "embarrassed"]

        for char in charArrayObj:
            if "Character Leaving: Character "+str(char.num) in rawOutput:
                char.withPlayer = False
            for clothing in clothingStyles:
                if "Character Change Clothes "+str(char.num)+": "+clothing in rawOutput:
                    char.clothing = clothing
            for emotion in emotions:
                if "Character Emotion "+str(char.num)+": "+emotion in rawOutput:       
                    char.emotion = emotion
            if "Interaction Intimacy Rating "+str(char.num)+": " in rawOutput:
                rating = int(rawOutput.split("Interaction Intimacy Rating "+str(char.num)+": ")[1].split("\n")[0].strip())
                affectionAddition = 2 * ((10*rating) / char.affection) * ((10*rating) / char.affection)
                if affectionAddition > 5:
                    affectionAddition = 5
                char.affection += affectionAddition
                if char.affection > 100:
                    char.affection = 100
            if char.withPlayer:
                charArrayWithPlayerNums.append(char.num)

        for charNum in charArrayWithPlayerNums:
            for char in charArrayObj:
                if char.num == charNum:
                    charImgLocation = output_dir.as_posix()+f"/charImages/char_{str(char.num)}_{char.clothing}_{char.emotion}_trimmed.png"
                    charImgLocationStr = str(url_for('static', filename = charImgLocation))
                    charArrayWithPlayerFileLocations.append(charImgLocationStr)

    move_to_location_script = '''
        const promptText = document.getElementById('prompt-textarea').value;
        const jailbreakText = document.getElementById('jailbreak-input').value;
        const proxyURL = document.getElementById('proxy-url-input').value
        const proxyPassword = document.getElementById('proxy-password-input').value
        const claudePrefill = document.getElementById('prefill-input').value
        const maxChars = document.getElementById('max-characters-input').value
        const model = document.getElementById('model-select').value
        fetch('/move_to', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ location: `{location}`,
            prompt: promptText,
            jailbreak: jailbreakText,
            proxyURL: proxyURL,
            proxyPassword: proxyPassword,
            prefill: claudePrefill,
            maxChars: maxChars,
            model: model
            })
        }).then(response => response.json())
        .then(result => {
            document.getElementById('background-image').src = result.backgroundFilePath;
            document.getElementById('current-time').textContent = `Current Time: ${result.currentTime}`;
            document.getElementById('current-clothes').textContent = `Current Clothes: ${result.currentClothing}`;
            document.getElementById('current-location').textContent = `Current Location: ${result.currentLocation}`;
            document.getElementById('text-output').innerHTML = `${result.textOutput}`;
            document.getElementById('buttons-container').innerHTML = result.buttons_html;
            
            // Clear previous character images
            const charContainer = document.getElementById('char-container');
            while (charContainer.firstChild) {
                charContainer.removeChild(charContainer.firstChild);
            }

            // Overlay new character images
            const charImages = result.charsToShow;
            const numImages = charImages.length;
            const screenHeight = window.innerHeight;
            const imgHeight = screenHeight * 0.9;
            const imgWidth = imgHeight * 0.684;
            const totalWidth = imgWidth * numImages;
            const startX = (window.innerWidth - totalWidth) / 2;

            charImages.forEach((charPath, index) => {
                const img = document.createElement('img');
                img.src = charPath;
                img.style.position = 'absolute';
                img.style.width = `${imgWidth}px`;
                img.style.height = `${imgHeight}px`;
                img.style.bottom = '0';
                img.style.left = `${startX + imgWidth * index}px`;
                charContainer.appendChild(img);
            });
        });
    '''.strip()

    currentOutput = textOutput


    return jsonify({
        'currentTime': currentTime,
        'currentClothing': currentClothing,
        'currentLocation': currentLocation,
        'textOutput': textOutput,
        'backgroundFilePath': backgroundFileStr,
        'charsToShow': charArrayWithPlayerFileLocations,
        'buttons_html': ''.join(
            f'<button type="button" class="move-button" data-location="{location}" onclick="{move_to_location_script.replace("{location}", location)}">{location}</button>'
            for location in currentAdjacentLocations
        )
    })

@app.route('/send_prompt', methods=['POST'])
def send_prompt():
    global currentLocation, currentAdjacentLocations, currentTime, currentClothing, currentTime, charArrayObj, charArrayWithPlayerNums, storySoFar, promptOpener, maxContextChars, currentOutput

    prompt_text = request.json.get('prompt')
    jailbreak = request.json.get('jailbreak')
    proxyURL = request.json.get('proxyURL')
    proxyPassword = request.json.get('proxyPassword')
    prefill = request.json.get('prefill')
    maxChars = request.json.get('maxChars')
    model = request.json.get('model')

    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword

    if len(maxChars) > 0:
        maxContextChars = maxChars

    currentTime = time_from_minutes(minutes_from_time(currentTime) + 2)
    storySoFar.append({"role": "user", "content": prompt_text})

    charArrayWithPlayerFileLocations = []
    charArrayWithPlayerNums = []

    charsAlreadyWithPlayer = []
    newArrivals = []
    for char in charArrayObj:
        if char.withPlayer:
            charsAlreadyWithPlayer.append(char)
        if not char.withPlayer and currentLocation == char.currentActivity(minutes_from_time(currentTime)).location:
            newArrivals.append(char)
            char.withPlayer = True

    newContent = ""
    if len(charsAlreadyWithPlayer) > 0:
        newContent += "The following characters have been present with "+playerName+". They may or may not still be present in the story."
        for char in charsAlreadyWithPlayer:
            newContent += char.name+" (character number "+str(char.num)+"). Their current clothing is "+char.clothing+" ("+char.clothingDescription[char.clothing]+"). Their immediate plans (if not already broken) are "+char.currentActivity(minutes_from_time(currentTime)).futurePlans+".\n"
    if len(newArrivals) > 0:
        newContent += "The following characters have just arrived to the same place as "+playerName+"."
        for char in newArrivals:
            char.clothing = char.currentActivity(minutes_from_time(currentTime)).clothing
            newContent += char.name+" (character number "+str(char.num)+") is performing (or about to perform) the activity: "+char.currentActivity(minutes_from_time(currentTime)).activity+". Their current clothing is "+char.currentActivity(minutes_from_time(currentTime)).clothing+" ("+char.clothingDescription[char.currentActivity(minutes_from_time(currentTime)).clothing]+"). Their immediate plans in the future are "+char.currentActivity(minutes_from_time(currentTime)).futurePlans+".\n" 

    charDescriptions = "Relevant character descriptions: "
    for char in charsAlreadyWithPlayer + newArrivals:
        charDescriptions += char.name+" (character number: "+str(char.num)+", character color code: "+char.color+"): "+char.personality+" Appearance: "+char.clothingDescription['charFaceAndBody']+"\n"
        if boolRomanticProgression:
            charDescriptions += char.name+"'s relationship with the player has updated based on previous interactions: "+relationshipDesc(char.affection, char.name)+"\n"

    newContent = newContent.strip()

    fixedContext = 0
    opener = "You are the narrator for a visual novel being played by the player, "+playerName+". Output what happens next along with any character dialogue and other requested information, correctly formatted."
    worldStuff = "Information about the world: "+worldInfo
    locationStuff = "The following are all the accessible locations in this world; any location you refer to must come from this list exactly: "+allLocationsStr
    playerStuff = "Information about the player: "+promptOpener+" The current time (in 24 hour format) is "+currentTime+", the player's current location is "+currentLocation+"("+get_location_text_description(locationArray, currentLocation)+") and the player's current clothing is "+currentClothing+"."
    instructionLength = 4282

    fixedContext += len(opener)+len(worldStuff)+len(locationStuff)+len(playerStuff)+len(charDescriptions)+len(newContent)+len(jailbreak)+instructionLength
    if model[:6] == "claude":
        fixedContext += len(prefill) + 85

    contextLeft = int(maxContextChars) - fixedContext
    storySoFar = trimContext(contextLeft, storySoFar)

    sendToAIJSON = [{"role": "system", "content": opener}]
    sendToAIJSON.append({"role": "system", "content": worldStuff})
    sendToAIJSON.append({"role": "system", "content": locationStuff})
    sendToAIJSON.append({"role": "system", "content": playerStuff})
    sendToAIJSON.append({"role": "system", "content": charDescriptions})
    sendToAIJSON += storySoFar
    sendToAIJSON.append({"role": "system", "content": newContent})

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(sendToAIJSON, temp_file)
        temp_file_path = temp_file.name

    AIresponse = None
    try:
        AIresponse = subprocess.run(['python', 'gen_text_prompt.py', temp_file_path, model, jailbreak, prefill, str(boolRomanticProgression)], capture_output=True, text=True)
    finally:
        os.remove(temp_file_path)
    rawOutput = AIresponse.stdout
    textOutput = rawOutput.split("Output:")[1].strip()
    storySoFar.append({"role": "assistant", "content": textOutput})

    currentOutput = textOutput

    clothingStyles = ["nude", "underwear", "swimsuit", "casual_clothes", "work_clothes"]
    emotions = ["neutral-happy", "laughing", "sad", "angry", "embarrassed"]

    for char in charArrayObj:
        if "Character Leaving: Character "+str(char.num) in rawOutput:
            char.withPlayer = False
        if not char.withPlayer:
            char.clothing = char.currentActivity(minutes_from_time(currentTime)).clothing
        for clothing in clothingStyles:
            if "Character Change Clothes "+str(char.num)+": "+clothing in rawOutput:
                char.clothing = clothing
        for emotion in emotions:
            if "Character Emotion "+str(char.num)+": "+emotion in rawOutput:       
                char.emotion = emotion
        if "Interaction Intimacy Rating "+str(char.num)+": " in rawOutput:
            rating = int(rawOutput.split("Interaction Intimacy Rating "+str(char.num)+": ")[1].split("\n")[0].strip())
            affectionAddition = 2 * ((10*rating) / char.affection) * ((10*rating) / char.affection)
            if affectionAddition > 5:
                affectionAddition = 5
            char.affection += affectionAddition
            if char.affection > 100:
                char.affection = 100
        if char.withPlayer:
            charArrayWithPlayerNums.append(char.num)

    if "Player Change Clothes:" in rawOutput:
        currentClothing = rawOutput.split("Player Change Clothes:")[1].split("\n")[0].strip()

    for charNum in charArrayWithPlayerNums:
        for char in charArrayObj:
            if char.num == charNum:
                charImgLocation = output_dir.as_posix()+f"/charImages/char_{str(char.num)}_{char.clothing}_{char.emotion}_trimmed.png"
                charImgLocationStr = str(url_for('static', filename = charImgLocation))
                charArrayWithPlayerFileLocations.append(charImgLocationStr)


    return jsonify({'currentTime': currentTime,
        'currentClothing': currentClothing,
        'textOutput': textOutput,
        'charsToShow': charArrayWithPlayerFileLocations
    })

@app.route('/save', methods=['POST'])
def save():
    fullSave = json.loads('{}')
    fullSave['playerName'] = playerName
    fullSave['playerDescription'] = playerDescription
    fullSave['output_dir'] = output_dir.as_posix()
    fullSave['boolRomanticProgression'] = str(boolRomanticProgression)
    fullSave['currentLocation'] = currentLocation
    fullSave['currentAdjacentLocations'] = currentAdjacentLocations
    fullSave['currentClothing'] = currentClothing
    fullSave['currentTime'] = currentTime
    fullSave['charArrayDict'] = charArrayDict

    fullSave['charArrayWithPlayerNums'] = charArrayWithPlayerNums
    fullSave['locationArray'] = locationArray
    fullSave['allLocationsStr'] = allLocationsStr
    fullSave['adjacencyMatrix'] = adjacencyMatrix
    fullSave['storySoFar'] = storySoFar
    fullSave['worldInfo'] = worldInfo
    fullSave['maxContextChars'] = maxContextChars
    fullSave['currentOutput'] = currentOutput

    fullSave['charArrayObj'] = []
    for char in charArrayObj:
        addChar = json.loads('{}')
        addChar['num'] = char.num
        addChar['name'] = char.name
        addChar['personality'] = char.personality
        addChar['defaultScheduleArray'] = char.defaultScheduleArray
        addChar['scheduleArray'] = char.scheduleArray
        addChar['affection'] = char.affection
        addChar['withPlayer'] = char.withPlayer
        addChar['clothing'] = char.clothing
        addChar['emotion'] = char.emotion
        addChar['color'] = char.color
        addChar['clothingDescription'] = char.clothingDescription
        fullSave['charArrayObj'].append(addChar)

    saves_dir = output_dir / "saves"
    saves_dir.mkdir(parents=True, exist_ok=True)

    n = 1
    save_file = None
    while True:
        save_file = saves_dir / f"save_{n}.txt"
        if not save_file.exists():
            with save_file.open('w') as f:
                json.dump(fullSave, f, indent=4)
            print(f"Created and wrote to file: {save_file}")
            break
        n += 1

    return jsonify({'saveName': str(save_file)})

def render_game_interface(textOutput, chars_html):
    backgroundFile = None
    for loc in locationArray:
        if loc['locationName'] == currentLocation:
            backgroundFile = getBackgroundFilePath(output_dir, loc, minutes_from_time(currentTime))    

    move_to_location_script = '''
        const promptText = document.getElementById('prompt-textarea').value;
        const jailbreakText = document.getElementById('jailbreak-input').value;
        const proxyURL = document.getElementById('proxy-url-input').value;
        const proxyPassword = document.getElementById('proxy-password-input').value;
        const claudePrefill = document.getElementById('prefill-input').value;
        const maxChars = document.getElementById('max-characters-input').value;
        const model = document.getElementById('model-select').value;
        fetch('/move_to', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ location: `{location}`,
            prompt: promptText,
            jailbreak: jailbreakText,
            proxyURL: proxyURL,
            proxyPassword: proxyPassword,
            prefill: claudePrefill,
            maxChars: maxChars,
            model: model
            })
        }).then(response => response.json())
        .then(result => {
            document.getElementById('background-image').src = result.backgroundFilePath;
            document.getElementById('current-time').textContent = `Current Time: ${result.currentTime}`;
            document.getElementById('current-clothes').textContent = `Current Clothes: ${result.currentClothing}`;
            document.getElementById('current-location').textContent = `Current Location: ${result.currentLocation}`;
            document.getElementById('text-output').innerHTML = `${result.textOutput}`;
            document.getElementById('buttons-container').innerHTML = result.buttons_html;
            document.getElementById('prompt-textarea').textContent = ``;
            document.getElementById('save-output').textContent = `If you aren't getting a response, just try resending. The AI may have screwed up the formatting.`;
            
            // Clear previous character images
            const charContainer = document.getElementById('char-container');
            while (charContainer.firstChild) {
                charContainer.removeChild(charContainer.firstChild);
            }

            // Overlay new character images
            const charImages = result.charsToShow;
            const numImages = charImages.length;
            const screenHeight = window.innerHeight;
            const imgHeight = screenHeight * 0.9;
            const imgWidth = imgHeight * 0.684;
            const totalWidth = imgWidth * numImages;
            const startX = (window.innerWidth - totalWidth) / 2;

            charImages.forEach((charPath, index) => {
                const img = document.createElement('img');
                img.src = charPath;
                img.style.position = 'absolute';
                img.style.width = `${imgWidth}px`;
                img.style.height = `${imgHeight}px`;
                img.style.bottom = '0';
                img.style.left = `${startX + imgWidth * index}px`;
                charContainer.appendChild(img);
            });
        });
    '''.strip()


    send_prompt_script = '''
        const promptText = document.getElementById('prompt-textarea').value;
        const jailbreakText = document.getElementById('jailbreak-input').value;
        const proxyURL = document.getElementById('proxy-url-input').value;
        const proxyPassword = document.getElementById('proxy-password-input').value;
        const claudePrefill = document.getElementById('prefill-input').value;
        const maxChars = document.getElementById('max-characters-input').value;
        const model = document.getElementById('model-select').value;
        fetch('/send_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: promptText,
            jailbreak: jailbreakText,
            proxyURL: proxyURL,
            proxyPassword: proxyPassword,
            prefill: claudePrefill,
            maxChars: maxChars,
            model: model
            })
        }).then(response => response.json())
        .then(result => {
            document.getElementById('text-output').innerHTML = `${result.textOutput}`;
            document.getElementById('current-time').textContent = `Current Time: ${result.currentTime}`;
            document.getElementById('current-clothes').textContent = `Current Clothes: ${result.currentClothing}`;
            document.getElementById('prompt-textarea').textContent = ``;
            document.getElementById('save-output').textContent = `If you aren't getting a response, just try resending. The AI may have screwed up the formatting.`;

            // Clear previous character images
            const charContainer = document.getElementById('char-container');
            while (charContainer.firstChild) {
                charContainer.removeChild(charContainer.firstChild);
            }

            // Overlay new character images
            const charImages = result.charsToShow;
            const numImages = charImages.length;
            const screenHeight = window.innerHeight;
            const imgHeight = screenHeight * 0.9;
            const imgWidth = imgHeight * 0.684;
            const totalWidth = imgWidth * numImages;
            const startX = (window.innerWidth - totalWidth) / 2;

            charImages.forEach((charPath, index) => {
                const img = document.createElement('img');
                img.src = charPath;
                img.style.position = 'absolute';
                img.style.width = `${imgWidth}px`;
                img.style.height = `${imgHeight}px`;
                img.style.bottom = '0';
                img.style.left = `${startX + imgWidth * index}px`;
                charContainer.appendChild(img);
            });
        });
    '''.strip()

    save_script = '''
        fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(result => {
            document.getElementById('save-output').textContent = `Saved in ${result.saveName}.`;
        });
    '''.strip()

    wait_uninterrupted_script = '''
        const waitTime = document.getElementById('wait-input').value;
        const maxChars = document.getElementById('max-characters-input').value;
        const proxyURL = document.getElementById('proxy-url-input').value;
        const proxyPassword = document.getElementById('proxy-password-input').value;
        fetch('/wait_uninterrupted', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ waitTime: waitTime,
            proxyURL: proxyURL,
            proxyPassword: proxyPassword,
            maxChars: maxChars
            })
        }).then(response => response.json())
        .then(result => {
            document.getElementById('current-time').textContent = `Current Time: ${result.currentTime}`;
            document.getElementById('wait-message').innerHTML = `${result.message}`;
            document.getElementById('text-output').innerHTML = `${result.textOutput}`;
        });
    '''.strip()

    wait_interrupted_script = '''
        const waitTime = document.getElementById('wait-input').value;
        const promptText = document.getElementById('prompt-textarea').value;
        const jailbreakText = document.getElementById('jailbreak-input').value;
        const proxyURL = document.getElementById('proxy-url-input').value;
        const proxyPassword = document.getElementById('proxy-password-input').value;
        const claudePrefill = document.getElementById('prefill-input').value;
        const maxChars = document.getElementById('max-characters-input').value;
        const model = document.getElementById('model-select').value;
        fetch('/wait_interrupted', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ waitTime: waitTime,
            jailbreak: jailbreakText,
            proxyURL: proxyURL,
            proxyPassword: proxyPassword,
            prefill: claudePrefill,
            maxChars: maxChars,
            model: model
            })
        }).then(response => response.json())
        .then(result => {
            document.getElementById('text-output').innerHTML = `${result.textOutput}`;
            document.getElementById('current-time').textContent = `Current Time: ${result.currentTime}`;
            document.getElementById('current-clothes').textContent = `Current Clothes: ${result.currentClothing}`;
            document.getElementById('wait-message').innerHTML = `${result.message}`;
            document.getElementById('save-output').textContent = `If you aren't getting a response, just try resending. The AI may have screwed up the formatting.`;

            // Clear previous character images
            const charContainer = document.getElementById('char-container');
            while (charContainer.firstChild) {
                charContainer.removeChild(charContainer.firstChild);
            }

            // Overlay new character images
            const charImages = result.charsToShow;
            const numImages = charImages.length;
            const screenHeight = window.innerHeight;
            const imgHeight = screenHeight * 0.9;
            const imgWidth = imgHeight * 0.684;
            const totalWidth = imgWidth * numImages;
            const startX = (window.innerWidth - totalWidth) / 2;

            charImages.forEach((charPath, index) => {
                const img = document.createElement('img');
                img.src = charPath;
                img.style.position = 'absolute';
                img.style.width = `${imgWidth}px`;
                img.style.height = `${imgHeight}px`;
                img.style.bottom = '0';
                img.style.left = `${startX + imgWidth * index}px`;
                charContainer.appendChild(img);
            });
        });
    '''.strip()

    buttons_html = ''.join(
        f'<button type="button" class="move-button" data-location="{location}" onclick="{move_to_location_script.replace("{location}", location)}">{location}</button>'
        for location in currentAdjacentLocations
    )
    backgroundFilePath = url_for('static', filename=backgroundFile + '.png')
    new_html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Game Interface</title>
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
            }}
            .image-container {{
                position: relative;
                width: 100%;
                height: 100vh;
                overflow: hidden;
            }}
            .image-container img {{
                width: 100%;
                height: 100%;
                object-fit: fill; /* Ensures the entire image fits the container */
                transition: opacity 1s ease-in-out;
            }}
            .info-container {{
                position: absolute;
                top: 10px;
                right: 10px;
                width: 200px; /* Adjusted width */
                background: rgba(0, 51, 102, 0.8); /* Darker blue color, partially transparent */
                padding: 10px;
                border-radius: 5px;
                color: white; /* White text */
                font-family: 'Open Sans', sans-serif; /* Readable font */
                font-size: 0.8em; /* Slightly smaller font size */
                text-shadow: 2px 2px 4px black; /* Black outline for text */
            }}
            .bottom-container {{
                position: absolute;
                bottom: 7%; /* 7% margin from bottom of the screen */
                left: 16.67%; /* 1/6th padding on the left */
                width: 66.66%; /* 2/3rds of the screen width */
                height: 22%; /* 22% of the screen height */
                background: rgba(0, 51, 102, 0.8); /* Darker blue color, partially transparent */
                padding: 5px 10px; /* 5px top and bottom padding, 10px left and right padding */
                text-align: center;
                border-radius: 5px;
                color: white; /* White text */
                font-size: 1.2em; /* Slightly larger font size */
                font-family: 'Open Sans', sans-serif; /* Readable font */
                text-shadow: 2px 2px 4px black; /* Black outline for text */
                overflow-y: auto; /* Scroll bar on overflow */
            }}
            .bottom-container p {{
                margin: 0; /* Remove default margin */
            }}
            .buttons-container {{
                margin-top: 10px;
            }}
            .buttons-container button {{
                display: block;
                margin: 5px 0;
            }}
            .input-container {{
                display: flex;
                justify-content: space-between;
                margin: 20px 0;
                padding: 0 10px;
            }}
            .input-left, .input-right {{
                width: 48%;
            }}
            .input-left textarea {{
                width: 100%;
                height: 100px;
            }}
            .input-left .large-input {{
                width: 100%;
                height: 50px;
                margin-top: 10px;
            }}
            .input-right {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}
            .input-right label {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .input-right textarea, .input-right select, .input-right .short-input {{
                width: 100%;
                height: 30px;
            }}
            .input-right .half-width {{
                width: 48%;
            }}
            .input-right .short-input {{
                width: 48%;
                height: 30px;
                margin-top: -8px; /* Adjusting vertical alignment */
            }}
            .flex-row {{
                display: flex;
                justify-content: space-between;
                gap: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="image-container">
            <img src="{backgroundFilePath}" alt="Landscape Image" id="background-image">
            <div id="char-container" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">{chars_html}</div>
            <div class="info-container" id="info-container">
                <p id="current-time">Current Time: {currentTime}</p>
                <p id="current-clothes">Current Clothes: {currentClothing}</p>
                <p id="current-location">Current Location: {currentLocation}</p>
                <div class="buttons-container" id="buttons-container">
                    {buttons_html}
                </div>
            </div>
            <div class="bottom-container">
                <p id="text-output">{textOutput}</p>
            </div>
        </div>
        <div class="input-container">
            <div class="input-left">
                <textarea id="prompt-textarea" placeholder="Prompt input..."></textarea>
                <br>
                <textarea id="jailbreak-input" class="large-input" placeholder="Jailbreak..."></textarea>
                <br>
                <button type="button" onclick="{send_prompt_script}">Submit</button>
                <button type="button" onclick="{save_script}">Save</button>
                <br>
                <p id="save-output" style="font-size: 12px; font-style: italic;"></p>
            </div>
            <div class="input-right">
                <div class="flex-row">
                    <div class="half-width">
                        <div class="label-container">
                            <label for="proxy-url-input">Endpoint URL:</label>
                        </div>
                        <textarea id="proxy-url-input" style="resize: both;">{given_url}</textarea>
                    </div>
                    <div class="half-width">
                        <div class="label-container">
                            <label for="proxy-password-input">API Key/Proxy Password:</label>
                        </div>
                        <textarea id="proxy-password-input" style="resize: both;">{given_password}</textarea>
                    </div>
                </div>
                <div class="flex-row">
                    <div class="half-width">
                        <div class="label-container">
                            <label for="model-select">Model:</label>
                        </div>
                        <select id="model-select" style="width: 100%;">
                            <option value="gpt-4o">gpt-4o</option>
                            <option value="gpt-4o-2024-05-13">gpt-4o-2024-05-13</option>
                            <option value="gpt-4-turbo">gpt-4-turbo</option>
                            <option value="gpt-4-turbo-2024-04-09">gpt-4-turbo-2024-04-09</option>
                            <option value="gpt-4-turbo-preview">gpt-4-turbo-preview</option>
                            <option value="gpt-4-0125-preview">gpt-4-0125-preview</option>
                            <option value="gpt-4-1106-preview">gpt-4-1106-preview</option>
                            <option value="gpt-4">gpt-4</option>
                            <option value="gpt-4-0613">gpt-4-0613</option>
                            <option value="gpt-4-0314">gpt-4-0314</option>
                            <option value="claude-3-5-sonnet-20240620">claude-3-5-sonnet-20240620</option>
                            <option value="claude-3-opus-20240229">claude-3-opus-20240229</option>
                            <option value="claude-3-sonnet-20240229">claude-3-sonnet-20240229</option>
                        </select>
                    </div>
                    <div class="half-width">
                        <div class="label-container">
                            <label for="max-characters-input">Max Content Size (in Characters):</label>
                        </div>
                        <input type="number" id="max-characters-input" style="width: 100%;" value="{maxContext}">
                    </div>
                </div>
                <div class="flex-row">
                    <div class="half-width">
                        <div class="label-container">
                            <label for="prefill-input">Prefill (Claude Only):</label>
                        </div>
                        <textarea id="prefill-input" style="resize: both; margin-top: 0px;" placeholder="Not recommended; it might screw with the intended formatting."></textarea>
                    </div>
                    <div class="half-width">
                        <div class="label-container">
                            <label for="wait-input">Wait (Minutes to Wait OR Time to Wait Until):</label>
                        </div>
                        <textarea id="wait-input" style="resize: both; margin-top: 0px;" placeholder="Your input should be either a number of minutes or a 24-hour time."></textarea>
                    </div>
                </div>
                <div class="flex-row">
                    <div class="half-width">
                    </div>
                    <div class="half-width">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div>
                                <button id="wait-interrupted" onclick="{wait_interrupted_script}">Wait until interrupted</button>
                                <button id="wait-uninterrupted" onclick="{wait_uninterrupted_script}">Wait without interruption</button>
                            </div>
                            <div style="font-size: small; font-style: italic;" id="wait-message"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            document.getElementById("model-select").value = model;
        }});
    </script>
    </html>
    '''.format(
        currentTime=currentTime,
        currentClothing=currentClothing,
        currentLocation=currentLocation,
        backgroundFilePath=backgroundFilePath,
        textOutput=textOutput,
        buttons_html=buttons_html,
        send_prompt_script=send_prompt_script,
        save_script=save_script,
        chars_html=chars_html,
        wait_uninterrupted_script=wait_uninterrupted_script,
        wait_interrupted_script=wait_interrupted_script,
        given_url = os.getenv('proxy_url', ''),
        given_password = os.getenv('proxy_password', ''),
        model = model if model is not None else "gpt-4o",
        maxContext = maxContextChars
    )
    return jsonify({'new_html': new_html_content})

@app.route('/load', methods=['POST'])
def load():
    global playerName, playerDescription, output_dir, currentLocation, currentAdjacentLocations, currentClothing, currentTime, charArrayDict, charArrayWithPlayerNums, locationArray, allLocationsStr, adjacencyMatrix, storySoFar, worldInfo, maxContextChars, currentOutput, charArrayObj, boolRomanticProgression
    refreshValues()

    playerName = request.json.get('playerName')
    playerDescription = request.json.get('playerDescription')
    output_dir = Path(request.json.get('output_dir'))
    boolRomanticProgression = (request.json.get('boolRomanticProgression') == "True")
    currentLocation = request.json.get('currentLocation')
    currentAdjacentLocations = request.json.get('currentAdjacentLocations')
    currentClothing = request.json.get('currentClothing')
    currentTime = request.json.get('currentTime')
    charArrayDict = request.json.get('charArrayDict')

    charArrayWithPlayerNums = request.json.get('charArrayWithPlayerNums')
    locationArray = request.json.get('locationArray')
    allLocationsStr = request.json.get('allLocationsStr')
    adjacencyMatrix = request.json.get('adjacencyMatrix')
    storySoFar = request.json.get('storySoFar')
    worldInfo = request.json.get('worldInfo')
    maxContextChars = request.json.get('maxContextChars')
    currentOutput = request.json.get('currentOutput')

    charArrayObj = []
    for char in request.json.get('charArrayObj'):
        character = Character(char['num'])
        character.name = char['name']
        character.personality = char['personality']
        character.defaultScheduleArray = char['defaultScheduleArray']
        character.scheduleArray = char['scheduleArray']
        character.affection = char['affection']
        character.withPlayer = char['withPlayer']
        character.clothing = char['clothing']
        character.emotion = char['emotion']
        character.color = char['color']
        character.clothingDescription = char['clothingDescription']
        charArrayObj.append(character)

    backgroundFilePath = None
    for loc in locationArray:
        if loc['locationName'] == currentLocation:
            backgroundFilePath = getBackgroundFilePath(output_dir, loc, minutes_from_time(currentTime))

    charArrayWithPlayerFileLocations = []
    for charNum in charArrayWithPlayerNums:
        for char in charArrayObj:
            if char.num == charNum:
                charImgLocation = str(output_dir)+f"/charImages/char_{str(char.num)}_{char.clothing}_{char.emotion}_trimmed.png"
                charImgLocationStr = str(url_for('static', filename = charImgLocation))
                charArrayWithPlayerFileLocations.append(charImgLocationStr)

    screen_height = "100vh"
    img_height_ratio = 0.9
    img_width_ratio = 0.684

    img_height = f"{img_height_ratio * 100}vh"
    img_width = f"calc({img_height} * {img_width_ratio})"
    num_images = len(charArrayWithPlayerFileLocations)
    total_width = f"calc({img_width} * {num_images})"
    start_x = f"calc((100vw - {total_width}) / 2)"

    chars_html = ""
    for index, char_path in enumerate(charArrayWithPlayerFileLocations):
        left_position = f"calc({start_x} + {index} * {img_width})"
        img_html = f'<img src="{char_path}" class="char-image" style="width: {img_width}; height: {img_height}; left: {left_position}; bottom: 0; position: absolute;">'
        chars_html += img_html    

    return render_game_interface(currentOutput, chars_html)

@app.route('/wait_uninterrupted', methods=['POST'])
def wait_uninterrupted():
    global currentTime, maxContextChars, currentOutput, charArrayWithPlayerNums, storySoFar

    waitTime = request.json.get('waitTime')
    proxyURL = request.json.get('proxyURL')
    proxyPassword = request.json.get('proxyPassword')
    maxChars = request.json.get('maxChars')

    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword

    if len(maxChars) > 0:
        maxContextChars = maxChars
   
    if len(charArrayWithPlayerNums) > 0:
        return jsonify({'currentTime': currentTime,
            'message': "You can't wait while characters are present.",
            'textOutput': currentOutput
        })

    else:
        if ":" in waitTime:
            currentTime = waitTime
            storySoFar.append({"role": "system", "content": "The player waits until "+currentTime})
            currentOutput = "You wait until "+currentTime+"."
            return jsonify({'currentTime': currentTime,
                'message': "",
                'textOutput': currentOutput
            })

        else:
            waitTimeInt = int(waitTime)
            currentTime = time_from_minutes(minutes_from_time(currentTime) + waitTimeInt)
            currentOutput = "You wait "+waitTime+" minutes."
            storySoFar.append({"role": "system", "content": "The player waits "+waitTime+" minutes."})
            return jsonify({'currentTime': currentTime,
                'message': "",
                'textOutput': currentOutput
            })

@app.route('/wait_interrupted', methods=['POST'])
def wait_interrupted():
    global currentLocation, currentAdjacentLocations, currentTime, currentClothing, currentTime, charArrayObj, charArrayWithPlayerNums, storySoFar, promptOpener, maxContextChars, currentOutput

    waitTime = request.json.get('waitTime')
    jailbreak = request.json.get('jailbreak')
    proxyURL = request.json.get('proxyURL')
    proxyPassword = request.json.get('proxyPassword')
    prefill = request.json.get('prefill')
    maxChars = request.json.get('maxChars')
    model = request.json.get('model')

    if len(proxyURL) > 0:
        os.environ['proxy_url_gpt'] = proxyURL + "/chat/completions"
        os.environ['proxy_url_claude'] = proxyURL + "/messages"
    if len(proxyPassword) > 0:
        os.environ['proxy_password'] = proxyPassword

    if len(maxChars) > 0:
        maxContextChars = maxChars

    waitTimeInt = 0
    if ":" in waitTime:
        waitTimeInt = (minutes_from_time(waitTime) - minutes_from_time(currentTime)) % 1440    
    else:
        waitTimeInt = int(waitTime)

    if len(charArrayWithPlayerNums) > 0:

        charArrayWithPlayerFileLocations = []
        for charNum in charArrayWithPlayerNums:
            for char in charArrayObj:
                if char.num == charNum:
                    charImgLocation = str(output_dir)+f"/charImages/char_{str(char.num)}_{char.clothing}_{char.emotion}_trimmed.png"
                    charImgLocationStr = str(url_for('static', filename = charImgLocation))
                    charArrayWithPlayerFileLocations.append(charImgLocationStr)

        return jsonify({'currentTime': currentTime,
            'message': "You can't wait while characters are present.",
            'textOutput': currentOutput,
            'currentClothing': currentClothing,
            'charsToShow': charArrayWithPlayerFileLocations
        })

    else:

        counter = 0
        charsAppear = False
        while counter < waitTimeInt:
            currentTime = time_from_minutes(minutes_from_time(currentTime) + 1)
            for char in charArrayObj:
                if currentLocation == char.currentActivity(minutes_from_time(currentTime)).location:
                    charsAppear = True
                    break
            if charsAppear:
                break
            else:
                counter += 1

        if counter == waitTimeInt:
            currentOutput = "You wait "+str(waitTimeInt)+" minutes. But nobody came."
            storySoFar.append({"role": "system", "content": "The player waits "+str(waitTimeInt)+" minutes. Nobody comes."})

            return jsonify({'currentTime': currentTime,
                'message': "",
                'textOutput': currentOutput,
                'currentClothing': currentClothing,
                'charsToShow': []
            })

        else:

            charArrayWithPlayerFileLocations = []
            charArrayWithPlayerNums = []

            charsAlreadyWithPlayer = []
            newArrivals = []
            for char in charArrayObj:
                if char.withPlayer:
                    charsAlreadyWithPlayer.append(char)
                if not char.withPlayer and currentLocation == char.currentActivity(minutes_from_time(currentTime)).location:
                    newArrivals.append(char)
                    char.withPlayer = True

            storySoFar.append({"role": "system", "content": "The player waits "+str(counter + 1)+" minutes."})       

            newContent = ""
            if len(charsAlreadyWithPlayer) > 0:
                newContent += "The following characters have been present with "+playerName+". They may or may not still be present in the story."
                for char in charsAlreadyWithPlayer:
                    newContent += char.name+" (character number "+str(char.num)+"). Their current clothing is "+char.clothing+" ("+char.clothingDescription[char.clothing]+"). Their immediate plans (if not already broken) are "+char.currentActivity(minutes_from_time(currentTime)).futurePlans+".\n"
            if len(newArrivals) > 0:
                newContent += "The following characters have just arrived to the same place as "+playerName+" while they were waiting."
                for char in newArrivals:
                    char.clothing = char.currentActivity(minutes_from_time(currentTime)).clothing
                    newContent += char.name+" (character number "+str(char.num)+") is performing (or about to perform) the activity: "+char.currentActivity(minutes_from_time(currentTime)).activity+". Their current clothing is "+char.currentActivity(minutes_from_time(currentTime)).clothing+" ("+char.clothingDescription[char.currentActivity(minutes_from_time(currentTime)).clothing]+"). Their immediate plans in the future are "+char.currentActivity(minutes_from_time(currentTime)).futurePlans+".\n" 

            charDescriptions = "Relevant character descriptions: "
            for char in charsAlreadyWithPlayer + newArrivals:
                charDescriptions += char.name+" (character number: "+str(char.num)+", character color code: "+char.color+"): "+char.personality+" Appearance: "+char.clothingDescription['charFaceAndBody']+"\n"
                if boolRomanticProgression:
                    charDescriptions += char.name+"'s relationship with the player has updated based on previous interactions: "+relationshipDesc(char.affection, char.name)+"\n"

            newContent = newContent.strip()

            fixedContext = 0
            opener = "You are the narrator for a visual novel being played by the player, "+playerName+". Output what happens next along with any character dialogue and other requested information, correctly formatted."
            worldStuff = "Information about the world: "+worldInfo
            locationStuff = "The following are all the accessible locations in this world; any location you refer to must come from this list exactly: "+allLocationsStr
            playerStuff = "Information about the player: "+promptOpener+" The current time (in 24 hour format) is "+currentTime+", the player's current location is "+currentLocation+"("+get_location_text_description(locationArray, currentLocation)+") and the player's current clothing is "+currentClothing+"."
            instructionLength = 3319

            fixedContext += len(opener)+len(worldStuff)+len(locationStuff)+len(playerStuff)+len(charDescriptions)+len(newContent)+len(jailbreak)+instructionLength
            if model[:6] == "claude":
                fixedContext += len(prefill) + 85

            contextLeft = int(maxContextChars) - fixedContext
            storySoFar = trimContext(contextLeft, storySoFar)
  
            sendToAIJSON = [{"role": "system", "content": opener}]
            sendToAIJSON.append({"role": "system", "content": worldStuff})
            sendToAIJSON.append({"role": "system", "content": locationStuff})
            sendToAIJSON.append({"role": "system", "content": playerStuff})
            sendToAIJSON.append({"role": "system", "content": charDescriptions})
            sendToAIJSON += storySoFar
            sendToAIJSON.append({"role": "system", "content": newContent})

            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
                json.dump(sendToAIJSON, temp_file)
                temp_file_path = temp_file.name

            AIresponse = None
            try:
                AIresponse = subprocess.run(['python', 'gen_text_prompt.py', temp_file_path, model, jailbreak, prefill, str(boolRomanticProgression)], capture_output=True, text=True)
            finally:
                os.remove(temp_file_path)
            rawOutput = AIresponse.stdout
            textOutput = rawOutput.split("Output:")[1].strip()
            storySoFar.append({"role": "assistant", "content": textOutput})

            currentOutput = textOutput

            clothingStyles = ["nude", "underwear", "swimsuit", "casual_clothes", "work_clothes"]
            emotions = ["neutral-happy", "laughing", "sad", "angry", "embarrassed"]

            for char in charArrayObj:
                if "Character Leaving: Character "+str(char.num) in rawOutput:
                    char.withPlayer = False
                if not char.withPlayer:
                    char.clothing = char.currentActivity(minutes_from_time(currentTime)).clothing
                for clothing in clothingStyles:
                    if "Character Change Clothes "+str(char.num)+": "+clothing in rawOutput:
                        char.clothing = clothing
                for emotion in emotions:
                    if "Character Emotion "+str(char.num)+": "+emotion in rawOutput:       
                        char.emotion = emotion
                if "Interaction Intimacy Rating "+str(char.num)+": " in rawOutput:
                    rating = int(rawOutput.split("Interaction Intimacy Rating "+str(char.num)+": ")[1].split("\n")[0].strip())
                    affectionAddition = 2 * ((10*rating) / char.affection) * ((10*rating) / char.affection)
                    if affectionAddition > 5:
                        affectionAddition = 5
                    char.affection += affectionAddition
                    if char.affection > 100:
                        char.affection = 100
                if char.withPlayer:
                    charArrayWithPlayerNums.append(char.num)

            if "Player Change Clothes:" in rawOutput:
                currentClothing = rawOutput.split("Player Change Clothes:")[1].split("\n")[0].strip()

            for charNum in charArrayWithPlayerNums:
                for char in charArrayObj:
                    if char.num == charNum:
                        charImgLocation = output_dir.as_posix()+f"/charImages/char_{str(char.num)}_{char.clothing}_{char.emotion}_trimmed.png"
                        charImgLocationStr = str(url_for('static', filename = charImgLocation))
                        charArrayWithPlayerFileLocations.append(charImgLocationStr)


            return jsonify({'currentTime': currentTime,
                'currentClothing': currentClothing,
                'textOutput': textOutput,
                'charsToShow': charArrayWithPlayerFileLocations,
                'message': ""
            })                 
    
if __name__ == '__main__':
    app.run(debug=True)
