from diffusers import StableDiffusionPipeline
import hashlib
import torch
from discord.ext import commands
import discord

class AnimeDiff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = "dreamlike-art/dreamlike-anime-1.0"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float32)

    @commands.command()
    async def animediff(self, ctx, *, prompt_input):
        """Generates an image using the AnimeDiff model."""
        prompt = "anime, masterpiece, high quality, high resolution " + prompt_input
        negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'

        image = await self.generate_image(prompt, negative_prompt)

        # Generate the MD5 hash of the image data
        hash_object = hashlib.md5(image.tobytes())
        filename = hash_object.hexdigest() + ".png"

        # Save the image with the hashed filename
        image.save("./" + filename)

        await ctx.send(file=discord.File(filename))

    async def generate_image(self, prompt, negative_prompt):
        return await self.bot.loop.run_in_executor(None, self.pipe, prompt, negative_prompt)

async def setup(bot):
    await bot.add_cog(AnimeDiff(bot))