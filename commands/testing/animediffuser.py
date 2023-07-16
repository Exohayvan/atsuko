from diffusers import StableDiffusionPipeline
import hashlib
import asyncio
from discord.ext import commands
import discord

class AnimeDiff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = "Linaqruf/anything-v3.0"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id)

    @commands.command()
    async def animediff(self, ctx, *, prompt_input):
        """Generates an image using the AnimeDiff model."""
        loop = asyncio.get_event_loop()
        image = await loop.run_in_executor(None, self.generate_image, prompt_input)

        # Generate the MD5 hash of the image data
        hash_object = hashlib.md5(image.tobytes())
        filename = hash_object.hexdigest() + ".png"

        # Save the image with the hashed filename
        image.save("./" + filename)

        await ctx.send(file=discord.File(filename))

    def generate_image(self, prompt_input):
        return self.pipe(prompt_input).images[0]

async def setup(bot):
    await bot.add_cog(AnimeDiff(bot))