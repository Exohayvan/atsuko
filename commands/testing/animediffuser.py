from discord.ext import commands
import discord
from diffusers import StableDiffusionPipeline
import torch
import hashlib
import random
import asyncio

class ImageGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = "dreamlike-art/dreamlike-anime-1.0"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float32)
        self.negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'

    @commands.command()
    async def generate_image(self, ctx, prompt: str):
        """Generates an image based on the provided prompt and sends the MD5 hash of the image data."""

        def generate_and_save_image():
            prompt = "anime, masterpiece, high quality, high resolution " + prompt
            image = self.pipe(prompt, negative_prompt=self.negative_prompt).images[0]

            # Generate the MD5 hash of the image data
            hash_object = hashlib.md5(image.tobytes())
            filename = hash_object.hexdigest() + ".png"

            # Save the image with the hashed filename
            image.save("./" + filename)

            return filename

        filename = await asyncio.to_thread(generate_and_save_image)

        # Send the hash to the user
        await ctx.send(f"The MD5 hash of your image is: {filename[:-4]}")

async def setup(bot):
    await bot.add_cog(ImageGenerator(bot))