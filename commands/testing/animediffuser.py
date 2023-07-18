import sqlite3
from discord import File
from discord.ext import commands
import discord
from diffusers import StableDiffusionPipeline
import torch
import hashlib
import asyncio
import os

DB_PATH = "./data/db/animediff.db"

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(e)
    if conn:
        return conn

def close_connection(conn):
    conn.close()

def create_table(conn):
    try:
        sql_create_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        user_id text NOT NULL,
                                        channel_id text NOT NULL,
                                        prompt text NOT NULL
                                    ); """
        c = conn.cursor()
        c.execute(sql_create_table)
    except sqlite3.Error as e:
        print(e)

def add_task(conn, task):
    sql = ''' INSERT INTO tasks(user_id,channel_id,prompt)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

    task_id = cur.lastrowid
    sql = ''' SELECT COUNT(*) FROM tasks WHERE id < ? '''
    cur.execute(sql, (task_id,))
    position = cur.fetchone()[0]
    
    return task_id, position + 1  # 1-indexed

def get_next_task(conn):
    sql = ''' SELECT * FROM tasks ORDER BY id ASC LIMIT 1 '''
    cur = conn.cursor()
    cur.execute(sql)
    task = cur.fetchone()
    return task

def delete_task(conn, task_id):
    sql = ''' DELETE FROM tasks WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, (task_id,))
    conn.commit()

class ImageGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = "dreamlike-art/dreamlike-anime-1.0"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float32)
        self.negative_prompt = 'simple background, duplicate, retro style, low quality, lowest quality, 1980s, 1990s, 2000s, 2005 2006 2007 2008 2009 2010 2011 2012 2013, bad anatomy, bad proportions, extra digits, lowres, username, artist name, error, duplicate, watermark, signature, text, extra digit, fewer digits, worst quality, jpeg artifacts, blurry'
        self.is_generating = False
        self.lock = asyncio.Lock()
        self.tasks = []  # Keep track of the tasks

        # Create database connection and table
        conn = create_connection()
        create_table(conn)
        close_connection(conn)

    @commands.command()
    async def animediff(self, ctx, *, prompt: commands.clean_content):
        """Generates an anime-style image based on the provided prompt and sends the MD5 hash of the image data."""
        
        conn = create_connection()
        task_id, position = add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), "anime, " + prompt))
        close_connection(conn)

        if not self.is_generating:
            self.process_queue()
        else:
            await ctx.send(f"Your request is queued. Position in queue: {position}. Estimated time: {position * 15} minutes.")

    @commands.command()
    async def dnddiff(self, ctx, *, prompt: commands.clean_content):
        """Generates an dnd-style image based on the provided prompt and sends the MD5 hash of the image data."""
        
        conn = create_connection()
        task_id, position = add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), "dungeons and dragons character, " + prompt))
        close_connection(conn)

        if not self.is_generating:
            self.process_queue()
        else:
            await ctx.send(f"Your request is queued. Position in queue: {position}. Estimated time: {position * 15} minutes.")

    @commands.command()
    async def imagediff(self, ctx, *, prompt: commands.clean_content):
        """Generates a realistic image based on the provided prompt and sends the MD5 hash of the image data."""
        
        conn = create_connection()
        task_id, position = add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), "image, realistic, " + prompt))
        close_connection(conn)

        if not self.is_generating:
            self.process_queue()
        else:
            await ctx.send(f"Your request is queued. Position in queue: {position}. Estimated time: {position * 15} minutes.")

    async def generate_and_send_image(self, ctx, prompt, task_id, user_id, channel_id):
        """Helper function to generate an image and send it to the user."""
    
        async with self.lock:
            def generate_and_save_image(prompt):
                full_prompt = "masterpiece, high quality, high resolution " + prompt
                image = self.pipe(full_prompt, negative_prompt=self.negative_prompt).images[0]
    
                # Generate the MD5 hash of the image data
                hash_object = hashlib.md5(image.tobytes())
                filename = hash_object.hexdigest() + ".png"
    
                # Save the image with the hashed filename
                image.save("./" + filename)
    
                return filename
    
            # Inform the user about the possible waiting time
            await ctx.send("Image generation is starting. It may take 10-20 minutes. If it takes longer, please try again.")
    
            # Generate the image
            filename = await asyncio.to_thread(generate_and_save_image, prompt)
    
            # Send the hash and the image to the user
            await ctx.send(f"The MD5 hash of your image is: {filename[:-4]}", file=File("./" + filename))
    
            # Add the task to the tasks list
            task = (task_id, user_id, channel_id, prompt)
            self.tasks.append(task)
    
            # Set is_generating to false and process the next task in the queue
            self.is_generating = False
            self.process_queue()
        
    def process_queue(self):
        """Helper function to process the next task in the queue."""

        conn = create_connection()
        task = get_next_task(conn)

        # If there are tasks in the queue, process the first one
        if task:
            self.is_generating = True
            task_id, user_id, channel_id, prompt = task
            channel = self.bot.get_channel(int(channel_id))
            delete_task(conn, task_id)

            # Generate and send the image for the next task in the queue
            asyncio.create_task(self.generate_and_send_image(channel, prompt))
    
        close_connection(conn)
        
    @commands.Cog.listener()
    async def on_ready(self):
        conn = create_connection()
        create_table(conn)
        task = get_next_task(conn)
        close_connection(conn)
        if task:
            self.is_generating = True
            task_id, user_id, channel_id, prompt = task
            channel = self.bot.get_channel(int(channel_id))
            asyncio.create_task(self.generate_and_send_image(channel, prompt))
            
    def stop_subprocess(self):
        """Cancels all running tasks."""

        for task in self.tasks:
            task.cancel()

        # Clear the tasks list
        self.tasks = []

async def setup(bot):
    await bot.add_cog(ImageGenerator(bot))
