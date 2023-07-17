import sqlite3
from discord import File
from discord.ext import commands
import discord
from diffusers import StableDiffusionPipeline
import torch
import hashlib
import asyncio
import os

class Character:
    def __init__(self, name, race, character_class, level, gender, outfit_type, hair_color, eye_color, weapon_type, image_file=None):
        self.name = name
        self.race = race
        self.character_class = character_class
        self.level = level
        self.gender = gender
        self.outfit_type = outfit_type
        self.hair_color = hair_color
        self.eye_color = eye_color
        self.weapon_type = weapon_type
        self.image_file = image_file

class DND(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = {}
        self.model_id = "dreamlike-art/dreamlike-anime-1.0"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float32)
        self.negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'
        self.lock = asyncio.Lock()

    @commands.group(invoke_without_command=True)
    async def dnd(self, ctx):
        await ctx.send('D&D command group. Use !dnd create to create a character or !dnd show to show your character.')

@dnd.command()
async def create(self, ctx):
    user_id = str(ctx.message.author.id)
    if user_id in self.characters:
        await ctx.send(f"You already have a character '{self.characters[user_id].name}'. Use `{self.bot.command_prefix}dnd update` to update your character.")
    else:
        await ctx.send("What's your character's name?")
        name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        
        await ctx.send("What's your character's race?")
        race = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What's your character's class?")
        character_class = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What's your character's level?")
        level = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What's your character's gender?")
        gender = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What type of outfit does your character wear?")
        outfit_type = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What color is your character's hair?")
        hair_color = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What color are your character's eyes?")
        eye_color = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        await ctx.send("What type of weapon does your character wield?")
        weapon_type = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        prompt = f"{race.content} {gender.content} with {outfit_type.content}, {hair_color.content} hair, {eye_color.content} eyes, wielding {weapon_type.content}"
        filename = await self.generate_and_send_image(ctx, f"dungeons and dragons character, {prompt}")
        character = Character(name.content, race.content, character_class.content, level.content, gender.content, outfit_type.content, hair_color.content, eye_color.content, weapon_type.content, image_file=filename)
        self.characters[user_id] = character
        await ctx.send(f"Character '{name.content}' has been created successfully!")
        
    @dnd.command()
    async def show(self, ctx):
        user_id = str(ctx.message.author.id)
        if user_id not in self.characters:
            await ctx.send(f"You have no character. Use `{self.bot.command_prefix}dnd create` to create one.")
        else:
            character = self.characters[user_id]
            embed = discord.Embed(title=character.name, description=f"Level {character.level} {character.race} {character.character_class}")
            embed.add_field(name="Gender", value=character.gender, inline=True)
            embed.add_field(name="Outfit", value=character.outfit_type, inline=True)
            embed.add_field(name="Hair Color", value=character.hair_color, inline=True)
            embed.add_field(name="Eye Color", value=character.eye_color, inline=True)
            embed.add_field(name="Weapon", value=character.weapon_type, inline=True)
            embed.set_image(url="attachment://" + character.image_file)
            await ctx.send(file=discord.File(character.image_file, filename=character.image_file), embed=embed)

    async def generate_and_send_image(self, ctx, prompt):
        async with self.lock:
            def generate_and_save_image(prompt):
                full_prompt = "masterpiece, high quality, high resolution " + prompt
                image = self.pipe(full_prompt, negative_prompt=self.negative_prompt).images[0]

                hash_object = hashlib.md5(image.tobytes())
                filename = hash_object.hexdigest() + ".png"
                image.save(filename)
                return filename

            await ctx.send("Image generation is starting. It may take 10-20 minutes. If it takes longer, please try again.")
            filename = await asyncio.to_thread(generate_and_save_image, prompt)
            await ctx.send(f"The MD5 hash of your image is: {filename[:-4]}", file=File(filename))
            return filename

async def setup(bot):
    await bot.add_cog(DND(bot))