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
    return cur.lastrowid

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

    async def generate_image(self, task):
        def generate_and_save_image():
            full_prompt = "anime, masterpiece, high quality, high resolution " + task[3]
            image = self.pipe(full_prompt, negative_prompt=self.negative_prompt).images[0]

            # Generate the MD5 hash of the image data
            hash_object = hashlib.md5(image.tobytes())
            filename = hash_object.hexdigest() + ".png"

            # Save the image with the hashed filename
            image.save("./" + filename)

            return filename

        filename = await asyncio.to_thread(generate_and_save_image)

        # Delete the task from the database
        conn = create_connection()
        delete_task(conn, task[0])
        close_connection(conn)

        # Send the hash to the user
        channel = self.bot.get_channel(int(task[2]))
        await channel.send(f"The MD5 hash of your image is: {filename[:-4]}", file=File("./" + filename))

        self.is_generating = False

    @commands.command()
    async def animediff(self, ctx, prompt: str):
        """Generates an image based on the provided prompt and sends the MD5 hash of the image data."""

        conn = create_connection()
        if not self.is_generating:
            self.is_generating = True
            close_connection(conn)
            await self.generate_image((None, str(ctx.message.author.id), str(ctx.channel.id), prompt))
        else:
            add_task(conn, (str(ctx.message.author.id), str(ctx.channel.id), prompt))
            close_connection(conn)
            task_count = len(conn.execute('SELECT * FROM tasks').fetchall())
            estimated_wait = task_count * 15
            await ctx.send(f"Your image generation request has been queued. The estimated wait time is {estimated_wait} minutes. Sorry but I don't have the money to process everyone's images at once")

    @commands.Cog.listener()
    async def on_ready(self):
        conn = create_connection()
        create_table(conn)
        task = get_next_task(conn)
        close_connection(conn)
        if task:
            self.is_generating = True
            await self.generate_image(task)

async def setup(bot):
    await bot.add_cog(ImageGenerator(bot))