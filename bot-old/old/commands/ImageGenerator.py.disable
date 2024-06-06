import sqlite3
from discord import File
from discord.ext import commands
import discord
from diffusers import StableDiffusionPipeline
import torch
import hashlib
import asyncio
import os
import logging

logger = logging.getLogger('ImageGenerator.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/ImageGenerator.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("ImageGenerator Cog Loaded. Logging started...")

DB_PATH = "./data/db/imagegenerationqueue.db"

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

    @commands.command(usage="!animediff <prompt>, <another prompt>, so on")
    async def animediff(self, ctx, *, prompt: commands.clean_content):
        """Generates an anime-style image based on the provided prompt and sends the MD5 hash of the image data."""
        
        conn = create_connection()
        task_id, position = add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), "anime, " + prompt))
        close_connection(conn)

        if not self.is_generating:
            self.process_queue()
            logger.info(f"Request started: {ctx.message.auther.id} | {ctx.channel.id} | anime, {prompt}")
        else:
            await ctx.send(f"Your request is queued. Position in queue: {position}. Estimated time: {position * 15} minutes.")
            logger.info("Request queued: {ctx.message.auther.id} | {ctx.channel.id} | anime, {prompt}")

    @commands.command(usage="!dnddiff <prompt>, <another prompt>, so on")
    async def dnddiff(self, ctx, *, prompt: commands.clean_content):
        """Generates an dnd-style image based on the provided prompt and sends the MD5 hash of the image data."""
        
        conn = create_connection()
        task_id, position = add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), "dungeons and dragons character, " + prompt))
        close_connection(conn)

        if not self.is_generating:
            self.process_queue()
            logger.info("Request started: {ctx.message.auther.id} | {ctx.channel.id} | dungeons and dragons character, {prompt}")
        else:
            await ctx.send(f"Your request is queued. Position in queue: {position}. Estimated time: {position * 15} minutes.")
            logger.info("Request queued: {ctx.message.auther.id} | {ctx.channel.id} | dungeons and dragons character, {prompt}")

    @commands.command(usage="!imagediff <prompt>, <another prompt>, so on")
    async def imagediff(self, ctx, *, prompt: commands.clean_content):
        """Generates a realistic image based on the provided prompt and sends the MD5 hash of the image data."""
        
        conn = create_connection()
        task_id, position = add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), "image, realistic, " + prompt))
        close_connection(conn)

        if not self.is_generating:
            self.process_queue()
            logger.info("Request started: {ctx.message.auther.id} | {ctx.channel.id} | image, realistic, {prompt}")
        else:
            await ctx.send(f"Your request is queued. Position in queue: {position}. Estimated time: {position * 15} minutes.")
            logger.info("Request queued: {ctx.message.auther.id} | {ctx.channel.id} | image, realistic, {prompt}")

    async def generate_and_send_image(self, ctx, prompt, task_id, user_id, channel_id):
        """Helper function to generate an image and send it to the user."""
        try:
            async with self.lock:
                def generate_and_save_image(prompt):
                    full_prompt = "masterpiece, high quality, high resolution " + prompt
                    logger.info(f"Generation started: {prompt}")
                    image = self.pipe(full_prompt, negative_prompt=self.negative_prompt).images[0]
        
                    # Generate the MD5 hash of the image data
                    logger.info("Generating MD5 Hash.")
                    hash_object = hashlib.md5(image.tobytes())
                    filename = hash_object.hexdigest() + ".png"

                    logger.info(f"Filename: {filename}")
                    # Save the image with the hashed filename
                    image.save("./" + filename)
        
                    return filename
        
                # Inform the user about the possible waiting time
                await ctx.send("Image generation is starting. It may take 10-20 minutes. If it takes longer, please try again.")
        
                # Generate the image
                loop = asyncio.get_running_loop()
                future = loop.run_in_executor(None, generate_and_save_image, prompt)
                task = asyncio.ensure_future(future)
                self.tasks.append(task)  # Keep track of the task
                filename = await task
        
                # Send the hash and the image to the user
                logger.info("Sent file to user.")
                await ctx.send(f"The MD5 hash of your image is: {filename[:-4]}", file=File("./" + filename))
        
                #delete file after sending
                logger.info(f"Deleted file: {filename}")
                os.remove("./" + filename)
                
                # Set is_generating to false and process the next task in the queue
                self.is_generating = False
                self.process_queue()
        except asyncio.CancelledError:
            # Handle the cancellation here
            logger.warning("Task was cancelled")
        except Exception as e:
            # Handle other exceptions here
            logger.warning(f"An error occurred: {e}")
        
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
            task = asyncio.create_task(self.generate_and_send_image(channel, prompt, task_id, user_id, channel_id))
            task.set_name('ImageGeneratorTask')  # Name the task for later reference
                    
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
            asyncio.create_task(self.generate_and_send_image(channel, prompt, task_id, user_id, channel_id), name='ImageGeneratorTask')
                                    
    def cog_unload(self):
        self.stop_subprocess()

    def stop_subprocess(self):
        """Cancels all running tasks."""
        for task in self.tasks:
            task.cancel()

async def setup(bot):
    await bot.add_cog(ImageGenerator(bot))
