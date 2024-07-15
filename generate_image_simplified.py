import asyncio
import sys
from pathlib import Path

from example.boilerplate import API
from novelai_api.ImagePreset import ImageModel, ImagePreset, ImageResolution, UCPreset

async def gen_image(prompt, output_dir, file_name, isPortrait, seed=0):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    async with API() as api_handler:
        api = api_handler.api

        model = ImageModel.Anime_v3
        preset = ImagePreset.from_default_config(model)
        if seed != 0:
            preset.seed = seed
        if not isPortrait:
            preset.resolution = (1216, 832)

        async for _, img in api.high_level.generate_image(prompt, model, preset):
            (output_path / f"{file_name}.png").write_bytes(img)

    return "Image generated successfully."

if __name__ == "__main__":
    if len(sys.argv) > 5:
        prompt = sys.argv[1]
        output_dir = sys.argv[2]
        file_name = sys.argv[3]
        isPortrait = sys.argv[4].lower() == 'true'
        seed = int(sys.argv[5])
        result = asyncio.run(gen_image(prompt, output_dir, file_name, isPortrait, seed))
        print(result)