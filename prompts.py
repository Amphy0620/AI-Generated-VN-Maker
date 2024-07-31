def gen_world_prompt(playerInput, clothingLabelsStr, isCharWorkClothes):

    workClothesAddendum = ""
    if isCharWorkClothes == "True":
        workClothesAddendum = " (reasonably interpret charWorkClothes as school uniforms, etc. if necessary)"

    return ('''The user wants to create a visual novel with the following scenario: '''
+playerInput
+'''. In one to two paragraphs, reiterate and elaborate on that scenario, staying true to the requested details. Reinforce any specific requested details here; repeat them multiple times if necessary. 
    Your output should be formatted in strict JSON, as {{\"world_info\": \"[Your elaboration here]\"}}. DO NOT include formatting backticks or 'json'. DO NOT linebreak. Your elaboration should NOT include: references to characters, over-detailed visual descriptions, or any suggestions as to what the user 'should' be doing. 
    Following this, remembering to add a comma delimiter , after the world_info string, begin creating characters to populate the world. These characters should be in a JSON array called \"chars\". Their attributes should be \"charNumber\" (an integer which starts at 1 and increments with each character), \"charName\" (The full name; unless the user has otherwise specified, default to Japanese names), \"charPersonality\", \"charRelationshipWPlayer\", \"charFaceAndBody\", '''
+clothingLabelsStr
+'''and \"charColorCode\".
    charPersonality should be a 3 to 4 paragraph prose string: The first paragraph should present two or three contrasting but complementary major personality features. For example: charName is prideful and stubborn but unusually horny, or charName is quiet and soft-spoken but can also be very direct. Explain in two or three sentences how these personality features manifest. The second paragraph should present a further two or three minor personality features, for example, charName has an unusually strong sense of smell, or charName is prone to rambling at length about nothing. Explain in another two or three sentences how these additional minor personality features interact with those previously given. Finally, the last one or two paragraphs should be the character's backstory. Briefly tell, starting from childhood and into present day, the character's life story and how they became who they are. Be creative and unique with the personalities! Also, describe potential relationships between characters here, such as charName1 and charName2 are good friends, or sisters, or etc, and also potential relationships with the player. Finally, and very importantly, describe the character's manner of speech and any associated quirks; for example, a rich girl may speak haughtily, hohoho, or a catgirl may intersperse her speech with nya~, or a shy character might... talk very timidly... interesting speech quirks can really sell a character! Consider both positive and negative personality traits; don't be afraid to make a character mean, or angry, or vain, etc. if it's interesting. Have characters fill an interesting diversity of roles that might arise from the setting (unless the player says explicitly what they want). Finally, throughout the whole description, if applicable, elaborate on how the character might react to or interact with the sort of situations that may arise from the suggested scenario, being specific to the user's given prompt. Again, DON'T linebreak.
    charRelationshipWPlayer MUST be one of: strangers, acquaintances, friends, good friends, sexual tension, lovers, soulmates EXACTLY. Choose exactly one of these 7 options to copy; with no prior information, default to \"acquaintances\".
    charFaceAndBody should be a string listing booru-style tags that describe the character's looks and physique. For example, \"long hair, red hair, straight hair, blue eyes, medium breasts, ...\". It's especially important to fully describe the hair style/color/length (consider phrases like blunt bangs, parted bangs, ponytail, twintails, hair bun, etc; if the VN is anime-style, feel free to have a diversity of unnatural hair colors), eye color, and breast size. DO NOT describe clothes in charFaceAndBody; imagine you're just seeing them naked. Also include unique bodily features, like \"cat ears, cat tail\" for catgirls, etc. Only include accessories if you can imagine them wearing said accessories while naked; glasses, necklaces, plastic hairbands, wrist scrunchies, etc. are probably fine. Always begin charFaceAndBody with 1boy or 1girl depending on gender. DON'T include the following tags: \"pale skin\", anything muscular for girls. Importantly, if you're describing well-known anime or pop-culture characters, include the full name of the character in charFaceAndBody, for example, \"Hakurei Reimu\", etc.
    Finally, the last few clothing tags should also be strings of booru-style tags, but ONLY to describe the corresponding clothes'''
+workClothesAddendum
+'''. For example, a casual outfit (if one is needed) might be \"white t-shirt, denim short shorts, black plastic hairband, ...\". It's important to be as descriptive as possible with these, in particular, ALWAYS include the color of any item. Also inclue bare 'body part' if the outfit doesn't cover it; for example, a bikini would probably have 'bare stomach', or a sleeveless top 'bare arms'. Don't include descriptions of shoes or socks, or anything below the thigh.
    charColorCode is the hex triplet of a color associated to that character, for example, \"#C0FF00\" for lime green. Make this different for each character; whatever color you choose, make it bright, as it'll be against a dark background.
    Remember again to repeatedly reinforce the details of the world that the player has provided, both in the world_info and also in descriptions of how characters may interact with the scenario of the prompt.''')



def gen_world_continue_prompt(playerInput, worldInfo, previousChars, clothingLabelsStr, isCharWorkClothes):

    workClothesAddendum = ""
    if isCharWorkClothes == "True":
        workClothesAddendum = " (reasonably interpret charWorkClothes as school uniforms, etc. if necessary)"

    return ('''The user wants to create a visual novel with the following scenario: '''
+playerInput
+'''. Here's an elaboration on that scenario: '''
+worldInfo
+'''. Continue creating characters to populate the world.
    These characters should be dictionaries in a JSON array. Their attributes should be \"charNumber\" (an integer which increments with each character), \"charName\" (The full name; unless the user has otherwise specified, default to Japanese names), \"charPersonality\", \"charRelationshipWPlayer\", \"charFaceAndBody\", '''
+clothingLabelsStr
+'''and \"charColorCode\".
    charPersonality should be a 3 to 4 paragraph prose string: The first paragraph should present two or three contrasting but complementary major personality features. For example: charName is prideful and stubborn but unusually horny, or charName is quiet and soft-spoken but can also be very direct. Explain in two or three sentences how these personality features manifest. The second paragraph should present a further two or three minor personality features, for example, charName has an unusually strong sense of smell, or charName is prone to rambling at length about nothing. Explain in another two or three sentences how these additional minor personality features interact with those previously given. Finally, the last one or two paragraphs should be the character's backstory. Briefly tell, starting from childhood and into present day, the character's life story and how they became who they are. Be creative and unique with the personalities! Also, describe potential relationships between characters here, such as charName1 and charName2 are good friends, or sisters, or etc, and also potential relationships with the player. Finally, and very importantly, describe the character's manner of speech and any associated quirks; for example, a rich girl may speak haughtily, hohoho, or a catgirl may intersperse her speech with nya~, or a shy character might... talk very timidly... interesting speech quirks can really sell a character! Consider both positive and negative personality traits; don't be afraid to make a character mean, or angry, or vain, etc. if it's interesting. Have characters fill an interesting diversity of roles that might arise from the setting (unless the player says explicitly what they want). Finally, throughout the whole description, if applicable, elaborate on how the character might react to or interact with the sort of situations that may arise from the suggested scenario, being specific to the user's given prompt. Again, DON'T linebreak.
    charRelationshipWPlayer MUST be one of: strangers, acquaintances, friends, good friends, sexual tension, lovers, soulmates EXACTLY. Choose exactly one of these 7 options to copy; with no prior information, default to \"acquaintances\".
    charFaceAndBody should be a string listing booru-style tags that describe the character's looks and physique. For example, \"long hair, red hair, straight hair, blue eyes, medium breasts, ...\". It's especially important to fully describe the hair style/color/length (consider phrases like blunt bangs, parted bangs, ponytail, twintails, hair bun, etc; if the VN is anime-style, feel free to have a diversity of unnatural hair colors), eye color, and breast size. DO NOT describe clothes in charFaceAndBody; imagine you're just seeing them naked. Also include unique bodily features, like \"cat ears, cat tail\" for catgirls, etc. Only include accessories if you can imagine them wearing said accessories while naked; glasses, necklaces, plastic hairbands, wrist scrunchies, etc. are probably fine. Always begin charFaceAndBody with 1boy or 1girl depending on gender. DON'T include the following tags: \"pale skin\", anything muscular for girls. Importantly, if you're describing well-known anime or pop-culture characters, include the full name of the character in charFaceAndBody, for example, \"Hakurei Reimu\", etc.
    Finally, the last few clothing tags should also be strings of booru-style tags, but ONLY to describe the corresponding clothes'''
+workClothesAddendum
+'''. For example, a casual outfit (if one is needed) might be \"white t-shirt, denim short shorts, black plastic hairband, ...\". It's important to be as descriptive as possible with these, in particular, ALWAYS include the color of any item. Also inclue bare 'body part' if the outfit doesn't cover it; for example, a bikini would probably have 'bare stomach', or a sleeveless top 'bare arms'. Don't include descriptions of shoes or socks, or anything below the thigh.
    charColorCode is the hex triplet of a color associated to that character, for example, \"#C0FF00\" for lime green. Make this different for each character; whatever color you choose, make it bright, as it'll be against a dark background.
    Remember again to repeatedly reinforce the details of the world that the player has provided in descriptions of how characters may interact with the scenario of the prompt. This character creation is a continuation of previous work; here are the characters already generated: '''
+previousChars
+'''. Note that this is in a JSON array, like your output should be, starting with [. As you're creating a continuation of this list, the charNumbers should begin their iteration from where this list ends. DO NOT copy the given list; start instead where the previously generated list ends.''')



def gen_location_prompt(worldInfo, isContinuation, previousLocations):

    continuePrompt = ""
    if (isContinuation == "True"):
        continuePrompt = f"\nThe array you're outputting is a continuation of previously generated locations. Because it's a continuation, the first locationNumber in your output should pick up where the last locationNumber left off rather than starting from 1. This is the array that you're continuing from: {previousLocations}\nContinue generating locations starting with the next locationNumber to fill out the parts of the world that these previous locations haven't reached, and end once you hit the designated final location number."

    return f'''We're creating a visual novel world based on the following world info and characters: {worldInfo}
    Output a JSON file which gives an array of locations for the player and character to move around. Each location should have attributes \"locationNumber\", \"locationName\", \"locationTextDescription\", \"locationTagDescription\", \"adjacentLocations\", \"isHubArea\" and \"isOutdoors\".
    isOutdoors really asks whether we need separate images for day and night skies; in weird or ambiguous cases like outer space, default to no.
    locationNumber starts at 1 and increments with each location.
    locationTextDescription briefly (no more than a sentence) describes the location in prose. locationTagDescription should be a brief list of objects and features of the location; for example, a bedroom might have \"bed, cabinet, tv\", a swimming pool might just have \"swimming pool\", an orbital space station might have \"planet, stars\"... essentially consider the list of objects the player should see at each location. These should be brief and only hit the essentials.
    adjacentLocations should be an array consisting of strings of other locationNames reachable from the current location; make the world somewhat interconnected, don't isolate locations too much!
    isHubArea is a boolean denoting whether that area is potentially a major crossroads at which the player can reach other hub areas; for example, if the setting is a small city, \"Downtown\" and \"Residential District\" might be hub areas, but not \"Classroom\" or \"Beach\". Important: Spread out connections over several hub areas; the bigger the world, the more hub areas.
    isOutdoors is a true or false boolean.
    When creating locations, consider not just the world itself but the characters inhabiting it; where might they go and what might they do? In particular, each character should have their own house or other living quarters (unless the scenario contradicts that). Don't forget to give the player their own place too (if necessary). Be exhaustive; for example, a small town might have a school with many different rooms, a residential area with everyone's house, a downtown with many businesses, a park, and so on. Building interiors should also have a realistic variety of rooms; standard living spaces have bathrooms and bedrooms; schools especially have club rooms, classrooms, gyms, so on. Modern personal living spaces should have a separate bathroom, if applicable. Less detailed worlds might have fewer locations (a deserted island, for instance), but you should still come up with a lot. You should be giving at least several dozen locations. Consider all parts of the characters' day; where do they sleep? Where do they shower? Work, play, go out? Fill out the world with both practical locations and fun 'extra' locations. All locations should have at least one adjacent location; try to make the world fully connected. {continuePrompt}
DON'T include backticks or 'json' formatting, just the raw json output; the very first character in your output should be an open square bracket [.'''



def gen_schedule_prompt(worldInfo, clothingNamesStr, isCharWorkClothes):

    workClothesAddendum = ""
    if isCharWorkClothes == "True":
        workClothesAddendum = " (work_clothes also may include school uniforms, etc.) "

    return ('''Given the following visual novel character, world info, and locations: '''
+worldInfo+
'''    Construct a detailed schedule for the character, considering where they might go and what they might do at all points of the day. The output should be in the form of a JSON array, where each entry corresponds to a continuous activity. The attributes should be \"startTime\", \"location\", \"activity\", \"clothing\", and \"future_plans\", all strings.
    startTime should be given in 24 hour format, e.g. 17:30 for 5:30 PM; the activity is assumed to end once the next startTime begins. Feel free to vary startTimes, they can be more realistic than just every half hour.
    location MUST be one of the listed locationNames. activity is a description of what the character is doing; be moderately descriptive. The activity should be in present tense, e.g. \"sleeping\".
    clothing MUST come from one of the following set: '''
+clothingNamesStr
+'''. If none seem to fit the activity, just choose the closest one '''
+workClothesAddendum
+'''Do not put ANYTHING other than EXACTLY ONE of the strings '''
+clothingNamesStr
+''' here.
    future_plans should briefly describe anything important (if anything) the character has coming up, as well as the time it begins and whether it's low, medium or high priority; upcoming work or school would be important, leisure time less so. Make the schedules interesting and unique and highly dependent on the character's personality. The schedule will loop, so try to align the ending activity with the start. Include sleeping as an activity (if the character does sleep). Be EXTREMELY thorough in describing the schedule; when does the character eat? Shower? Change methods of study or relaxation? Successive activities in the schedule can still have the same location, like a character might be reading a book in the library for one activity but then doing homework in the library the next. Don't reference other characters when constructing these schedules or explicitly state that other characters are present. Feel free to use smaller increments of time, like 5-15 minutes per activity, in your quest to be thorough. DO NOT use backticks or 'json' to format the output, just give it in pure JSON.''')



def initialize_prompt(worldInfo, playerInfo):
    return f'''You're narrating a visual novel for the player; details and locations of this visual novel are provided here: {worldInfo}
    {playerInfo}
    First, choose a location among those provided for the player (using the exact locationName) to be initialized into the story as well as an initial time in 24 hour format (so 17:30 would represent 5:30 PM). Format this like so: On line 1, New location: locationName (exactly copied, without quotes). Then new line character \n, and on line 2, Current time: currentTime (again without quotes, in 24 hour format). Then new line character \n again, and on line 3, Current clothes: ... (give what the player is wearing at this time). Then \n again, and beginning with the fourth line, begin with Output: and then (still on line 4) become the narrator and introduce the player to the world.
    For example, New location: your_bedroom\nCurrent time: 07:40\nCurrent clothes: Boxer briefs\nOutput: Blah blah blah... [Try to keep this Output part under 400 characters.] Refer to the player in second person, as 'you', and give a modest description of the world they now find themselves in. The player should not be initialized around any characters; they should begin alone.'''



def romance_instructions():
    return ''' Furthermore, given the most recent interaction, for each character the player interacted with, on a new line, give an Interaction Intimacy Rating from 0 to 10 formatted like this: \nInteraction Intimacy Rating X: Y\n where X is again the relevant character number and Y is the rating.
    Use the following as a rough guide for what score to give:
    0: Negative interaction/No direct interaction.
    2: Polite conversation (talking about the weather, business, etc.)
    3: Friendly/informal conversation (talking about preferences, weekend plans, etc.)
    5: Personal conversation (talking about feelings, personal life, etc.), making them laugh
    6: Compliments, flirty/teasing conversation, doing a favor
    7: Casual intimacy/sex appeal (hand-holding, being unusually close, light skinship, ...)
    8: Date, romance, kissing
    10: Close physical intimacy, third base and beyond...'''



def romance_example():
    return "Interaction Intimacy Rating 1: 4\nInteraction Intimacy Rating 3: 2\n"



def button_input_instructions(boolRomanticProgression, clothingNamesStr, emotionNamesStr):
    romanceInstructions = ""
    romanceExample = ""
    if boolRomanticProgression == "True":
        romanceInstructions = romance_instructions()
        romanceExample = romance_example()
    return ('''Do not speak for or otherwise perform actions for the player; your job is to control only the other characters and the surrounding world. Always refer to the player in the second person, as 'you'.
    Firstly, write Output: , and then give a brief output text for the VN based on what the player has done and what the characters are doing. Include character dialogue if necessary. Any time a character's name and/or dialogue appears, encase it all in <span style=\"color: [hex code];\"></span>, where [hex code] is the color corresponding to that character. Encase BOTH the character's name and their dialogue. If the Output is longer than 400 or so characters (which it doesn't have to be), break it into chunks of less than 400 characters using '//' as a break; for example, [blah blah] // [blah blah] // [blah blah], where each [blah blah] is no more than 400 characters. When the output is finished, go to a new line, and on that new line write END OUTPUT (all caps). 
    After END OUTPUT, again go to a new line, and output the following information, if applicable, formatted exactly and based on your output: If a character present with the player before the move is no longer present due to the player's movement, output on its own line Character Leaving: Character X, where X is the number associated to the leaving character. If multiple characters are leaving, use multiple lines. This will remove the character from the story progression, so only do this if you're sure the player and the character are separating; don't do this if the character is following the player or the interaction with the player is otherwise continuing.
    For every character still present in the story (either by following the player or by being newly met), output on its own line Character Emotion X: [emotion]. Here X is again the associated character number. [emotion] MUST be one of: '''
+emotionNamesStr
+'''; choose exactly one of these. The chosen emotion should be the option among these that comes closest to their emotion conveyed in the output.'''
+romanceInstructions
+ ''' Furthermore, if any of the characters still present have changed clothes from their previous clothes, output again on its own line Character Change Clothes X: [new clothing type]. Here [new clothing type] must be exactly one of: '''
+clothingNamesStr
+''', exactly as written. Again, it's only necessary to do this if the character has just now changed clothes from what they had on previously.
    Finally, after all of the information is presented, go to a final new line and write DONE (all caps).
    Here's an example output, with all data formatted properly; in this scenario, the player has left characters 2 and 4 behind, but characters 1 and 3 are (still) present, and character 3 has just changed into a new clothing style while character 1 hasn't changed clothes:
    Output: <span style=\"color: [hex code];\">[Charname]</span> comes up to you. <span style=\"color: [hex code];\">[Charname]: \"Hello!\"</span>... // ... // ...
END OUTPUT
Character Leaving: Character 2
Character Leaving: Character 4
Character Emotion 1: emotion
Character Emotion 3: emotion
'''
+romanceExample
+'''Character Change Clothes 3: new clothing style
DONE
    Note again that everything is on its own line, even the two different Character Leavings, and both character names and dialogue are contained in the color span.''')



def prompt_input_instructions(boolRomanticProgression, clothingNamesStr, emotionNamesStr):
    romanceInstructions = ""
    romanceExample = ""
    if boolRomanticProgression == "True":
        romanceInstructions = romance_instructions()
        romanceExample = romance_example()
    return ('''Do not speak for or otherwise perform actions for the player; your job is to control only the other characters and the surrounding world. Always refer to the player in the second person, as 'you'.
    Firstly, write Output: , and then give a brief few-sentence output text for the VN based on what the player has done and what the characters are doing. Include character dialogue if necessary. Any time a character's name and/or dialogue appears, encase it all in <span style=\"color: [hex code];\"></span>, where [hex code] is the color corresponding to that character. Encase BOTH the character's name and their dialogue. If the Output is longer than 400 or so characters (which it doesn't have to be), break it into chunks of less than 400 characters using '//' as a break; for example, [blah blah] // [blah blah] // [blah blah], where each [blah blah] is no more than 400 characters. When the output is finished, go to a new line, and on that new line write END OUTPUT (all caps). 
    After END OUTPUT, again go to a new line, and output the following information, if applicable, formatted exactly and based on yoru output: If a character present with the player before the move is no longer present due to leaving, output on its own line Character Leaving: Character X, where X is the number associated to the leaving character. If multiple characters are leaving, use multiple lines. If the character is, say, simply moving to an adjacent room, don't do this; only output Character Leaving if the character is now no longer present in the story.
    For every character now present in the story (either by still being with the player or by being newly met), output on its own line Character Emotion X: [emotion]. Here X is again the associated character number. [emotion] MUST be one of: '''
+emotionNamesStr
+'''; choose exactly one of these. The chosen emotion should be the option among these that comes closest to their emotion conveyed in the output.'''
+ romanceInstructions
+ ''' Furthermore, if any of the characters still present have changed clothes from their previous clothes, output again on its own line Character Change Clothes X: [new clothing type]. Here [new clothing type] must be exactly one of: '''
+clothingNamesStr
+''', exactly as written. Again, it's only necessary to do this if the character is just now changing clothes from what they had on.
    If the player has changed clothes, write on its own line Player Change Clothes: [new clothes]; for the player (unlike other characters), [new clothes] can be any description.
    Finally, after all of the information is presented, go to a final new line and write DONE (all caps).
    Here's an example output, with all data formatted properly; in this scenario, characters 2 and 4 have just left, but characters 1 and 3 are (still) present, and the player has just changed into their swimsuit while character 3 has changed clothes but character 1 hasn't changed clothes:
    Output: <span style=\"color: [hex code];\">[Charname]</span> comes up t you. <span style=\"color: [hex code];\">[Charname]: \"Hello!\"</span>... // ... // ...
END OUTPUT
Character Leaving: Character 2
Character Leaving: Character 4
Character Emotion 1: emotion
Character Emotion 3: emotion
'''
+romanceExample
+'''Character Change Clothes 3: new clothing style
Player Change Clothes: Blue swim trunks
DONE
    Note again that everything is on its own line, even the two different Character Leavings, and both character names and dialogue are contained in the color span, and the NPC's change of clothes comes specifically from the list '''
+clothingNamesStr
+''' while the player's change of clothes can be any description. Important: the player CANNOT change locations via this prompt; they must stay in and around the current location. The player also can't advance time via this prompt; the current time is given and fixed.''')