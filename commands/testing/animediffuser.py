import sqlite3
from discord.ext import commands
from discord import File
from diffusers import StableDiffusionPipeline
import torch
import hashlib
import asyncio

class ImageGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = "dreamlike-art/dreamlike-anime-1.0"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float32)
        self.negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'

        self.conn = sqlite3.connect('./data/db/animediff.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS jobs
                     (id INTEGER PRIMARY KEY, user TEXT, prompt TEXT)''')
        self.conn.commit()
        self.is_generating = False

    @commands.command()
    async def animediff(self, ctx, prompt: str):
        """Generates an image based on the provided prompt and sends the MD5 hash of the image data."""

        if self.is_generating:
            position = self.add_job(ctx.message.author.id, prompt)
            estimated_time = position * 15
            await ctx.send(f"Image generation is in progress. Your job is number {position} in the queue. Estimated waiting time is approximately {estimated_time} minutes.")
        else:
            self.is_generating = True
            await self.generate_image(ctx, prompt)
            self.is_generating = False
            await self.check_queue()

    def add_job(self, user, prompt):
        self.c.execute("INSERT INTO jobs (user, prompt) VALUES (?, ?)", (user, prompt))
        self.conn.commit()
        self.c.execute("SELECT COUNT(*) FROM jobs")
        return self.c.fetchone()[0]

    async def generate_image(self, ctx, prompt):
        def generate_and_save_image():
            full_prompt = "anime, masterpiece, high quality, high resolution " + prompt
            image = self.pipe(full_prompt, negative_prompt=self.negative_prompt).images[0]

            # Generate the MD5 hash of the image data
            hash_object = hashlib.md5(image.tobytes())
            filename = hash_object.hexdigest() + ".png"

            # Save the image with the hashed filename
            image.save("./" + filename)

            return filename

        filename = await asyncio.to_thread(generate_and_save_image)

        # Send the hash to the user
        await ctx.send(f"The MD5 hash of your image is: {filename[:-4]}", file=File("./" + filename))

    async def check_queue(self):
        self.c.execute("SELECT id, user, prompt FROM jobs ORDER BY id ASC LIMIT 1")
        job = self.c.fetchone()
        if job is not None:
            self.c.execute("DELETE FROM jobs WHERE id = ?", (job[0],))
            self.conn.commit()
            ctx = await self.bot.fetch_user(job[1])
            await self.generate_image(ctx, job[2])

async def setup(bot):
    await bot.add_cog(ImageGenerator(bot))