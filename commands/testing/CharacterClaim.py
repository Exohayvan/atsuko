import sqlite3
import discord
import concurrent.futures
from discord.ext import commands, tasks
from diffusers import StableDiffusionPipeline
import torch
import random
import os
import asyncio

class CharacterClaim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data/db/characterspawns/channels.db"
        self.characters_path = "./data/db/characterspawns/characters"
        self.active_character_id = None
        self.create_db()
        self.spawn_character_loop.start()

    def create_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS spawn_channels (
                            server_id TEXT PRIMARY KEY,
                            channel_id TEXT NOT NULL
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS claimed_characters (
                            character_id INTEGER PRIMARY KEY,
                            claimed_by TEXT
                          )''')
        conn.commit()
        conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setspawn(self, ctx):
        """Sets the spawn channel for character images to the channel where the command is invoked."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('REPLACE INTO spawn_channels (server_id, channel_id) VALUES (?, ?)', 
                       (str(ctx.guild.id), str(ctx.channel.id)))
        conn.commit()
        conn.close()
        await ctx.send(f"Spawn channel set to {ctx.channel.mention}")
    
    @tasks.loop(minutes=random.randint(20, 60))
    async def spawn_character_loop(self):
        await self.bot.wait_until_ready()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM spawn_channels')
        rows = cursor.fetchall()
        conn.close()
    
        for row in rows:
            server_id, channel_id = row
            channel = self.bot.get_channel(int(channel_id))
    
            if channel:
                try:
                    await self.spawn_character(channel)
                except Exception as e:
                    # Log the error here (e.g., print to console or write to a log file)
                    print(f"Error sending character to channel {channel_id}: {e}")
                else:
                    # Optional: Log successful delivery
                    print(f"Character successfully sent to channel {channel_id}")
    
                # Optional: Add a delay between each message to avoid rate limits
                await asyncio.sleep(0.5)

    async def spawn_character(self, channel):
        """Function to generate and post a character."""
        # If there is an active but unclaimed character, delete its file
        if self.active_character_id is not None:
            unclaimed_file_path = f"{self.characters_path}/{self.active_character_id}.png"
            if os.path.exists(unclaimed_file_path):
                os.remove(unclaimed_file_path)

        # Generate the prompt for the character
        prompt = self.generate_random_prompt()

        # Initialize the executor for running heavy computations
        executor = concurrent.futures.ThreadPoolExecutor()
        try:
            loop = asyncio.get_event_loop()

            # Define a function for initializing the pipeline
            def init_pipe():
                return StableDiffusionPipeline.from_pretrained("dreamlike-art/dreamlike-anime-1.0", torch_dtype=torch.float32)

            # Initialize the pipeline in the executor
            pipe = await loop.run_in_executor(executor, init_pipe)

            # Generate the image in the executor
            image = await loop.run_in_executor(executor, lambda: pipe(prompt).images[0])

            # Determine the next file name
            next_file_id = self.get_next_file_id()
            filename = f"{self.characters_path}/{next_file_id}.png"

            # Save the image
            image.save(filename)

            # Send the image to the designated channel
            message = await channel.send(f"Character ID: {next_file_id}", file=discord.File(filename))

            # Update the active character ID
            self.active_character_id = next_file_id

            # Add a reaction to the message for claiming
            await message.add_reaction('✅')
        finally:
            # Shutdown the executor after use
            executor.shutdown()

    def get_next_file_id(self):
        """Determines the next file ID based on existing files."""
        if not os.path.exists(self.characters_path):
            os.makedirs(self.characters_path)
        files = os.listdir(self.characters_path)
        file_ids = [int(f.split('.')[0]) for f in files if f.endswith('.png')]
        next_id = max(file_ids, default=0) + 1
        return next_id

    def generate_random_prompt(self):
        """Generates a random prompt for the character."""
        hair_colors = ["blue", "white", "red", "green"]
        genders = ["male", "female"]
        return f"{random.choice(hair_colors)} hair, {random.choice(genders)}"

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Listener for reactions to claim a character."""
        if user != self.bot.user and self.active_character_id is not None:
            message = reaction.message
            if message.attachments and self.active_character_id == int(os.path.splitext(message.attachments[0].filename)[0]):
                if self.claim_character(self.active_character_id, user.id):
                    await message.reply(f"{user.mention} has claimed character ID: {self.active_character_id}")
                    self.active_character_id = None
                else:
                    await message.reply("This character has already been claimed.")

    def claim_character(self, character_id, user_id):
        """Claims a character for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if the character is already claimed
        cursor.execute('SELECT * FROM claimed_characters WHERE character_id = ?', (character_id,))
        if cursor.fetchone() is not None:
            conn.close()
            return False

        # Claim the character
        cursor.execute('INSERT INTO claimed_characters (character_id, claimed_by) VALUES (?, ?)', 
                       (character_id, str(user_id)))
        conn.commit()
        conn.close()
        return True

    def cog_unload(self):
        self.spawn_character_loop.cancel()

async def setup(bot):
    await bot.add_cog(CharacterClaim(bot))
