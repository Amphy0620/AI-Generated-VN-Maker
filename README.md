# AI-Generated Visual Novel Maker

- Combines the freedom of AI chat roleplaying with the structure of a pre-programmed visual novel.
- Use a GPT or Claude API key for text generation and a NovelAI account for image generation.
- Run start.bat, let it install the dependencies, then open 127.0.0.1:5000 in your browser of choice.
- New generations will be created in generated_VNs/[your chosen world name] as soon as you hit 'Submit'; you can see the progress of file generation there.
- The generation process is segmented; start by filling out the form and clicking Step 1. When Step 1 finishes generating, a message will appear to that effect below the button, at which point you should check the generated file and move on to Step 2, etc.
- The final step (Step 4) is image generation, which takes by far the longest. As a baseline, expect ~1 hr generation time for a VN with 5 characters, 5 emotions, and 5 clothing styles; image generation isn't that fast and there's lots to make.
- If you change the name of the world folder, be sure to also change the output_dir in any save files it contains.
- Save files don't contain API keys or passwords; you can share generated VNs just by sharing the world folders.

## Image Generation

The image generation is based on [Aedial's NovelAI API](https://github.com/Aedial/novelai-api). There's almost certainly some bloat in this repo left over from that one, I wasn't that careful in figuring out only which files I absolutely require.

## Contributing

This code is a complete mess and I have no idea what I'm doing. I welcome anyone crazy enough to try to wrangle it.