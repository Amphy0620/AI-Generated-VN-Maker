# AI-Generated Visual Novel Maker

-Combines the freedom of AI chat roleplaying with the structure of a pre-programmed visual novel.
-Use a GPT or Claude API key for text generation and a NovelAI account for image generation.
-Run start.bat, let it install the dependencies, then open 127.0.0.1:5000 in your browser of choice.
-New generations will be created in generated_VNs/world_N as soon as you hit 'Submit'; you can see the progress of file generation there.
-If something breaks during generation, unfortunately you'll have to restart. This only really tends to happen at the very start if the AI's JSON isn't formatted properly; all the more reason to keep an eye on the world folder as it's generating.
-As a baseline, expect ~1 hr generation time for a 5-character VN; image generation isn't that fast and there's lots to make.
-If you change the name of the world_N folder, be sure to also change the output_dir in any save files it contains.
-Save files don't contain API keys or passwords; you can share generated VNs just by sharing the world folders.

## Image Generation

The image generation is based on [Aedial's NovelAI API](https://github.com/Aedial/novelai-api). I was lazy with figuring out exactly which files from there are necessary here, so there's definitely a lot of unused bloat left over in this repo from that one.

## Contributing

This code is a complete mess and I have no idea what I'm doing. I welcome anyone crazy enough to try to wrangle it.