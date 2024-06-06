from discord.ext import commands
import os
import aiohttp
import discord

class EmojiManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_folder = './data/emojis/'

    async def download_emoji(self, url, file_path):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())

    @commands.command(usage="!emoji_save <emoji1> <emoji2> ...")
    @commands.has_permissions(manage_guild=True)
    async def emoji_save(self, ctx, *emojis):
        """Saves multiple custom emojis to the local storage."""
        if not os.path.exists(self.emoji_folder):
            os.makedirs(self.emoji_folder)

        for emoji_str in emojis:
            # Parsing the custom emoji format
            if emoji_str.startswith("<") and emoji_str.endswith(">"):
                animated, emoji_name, emoji_id = False, '', ''
                split = emoji_str.strip('<>').split(':')
                if len(split) == 3:
                    animated, emoji_name, emoji_id = split[0] == 'a', split[1], split[2]
                
                if emoji_id.isdigit():
                    file_extension = 'gif' if animated else 'png'
                    file_path = os.path.join(self.emoji_folder, f"{emoji_name}.{file_extension}")
                    emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_extension}"

                    if not os.path.exists(file_path):
                        await self.download_emoji(emoji_url, file_path)
                        await ctx.send(f"Emoji {emoji_name} saved!")
                    else:
                        await ctx.send(f"Emoji {emoji_name} is already saved.")
                else:
                    await ctx.send(f"Invalid emoji format for {emoji_str}.")
            else:
                await ctx.send(f"Please provide a valid custom emoji for {emoji_str}.")
                            
    @commands.command(usage="!emoji_add <emoji1> <emoji2> ...")
    @commands.has_permissions(manage_guild=True)
    async def emoji_add(self, ctx, *emojis):
        """Saves multiple custom emojis to local storage and adds them to the server."""
        for emoji_str in emojis:
            if emoji_str.startswith("<") and emoji_str.endswith(">"):
                animated, emoji_name, emoji_id = False, '', ''
                split = emoji_str.strip('<>').split(':')
                if len(split) == 3:
                    animated, emoji_name, emoji_id = split[0] == 'a', split[1], split[2]

                if emoji_id.isdigit():
                    file_extension = 'gif' if animated else 'png'
                    file_path = os.path.join(self.emoji_folder, f"{emoji_name}.{file_extension}")
                    emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{file_extension}"

                    if not os.path.exists(file_path):
                        await self.download_emoji(emoji_url, file_path)

                    with open(file_path, 'rb') as emoji_file:
                        try:
                            await ctx.guild.create_custom_emoji(name=emoji_name, image=emoji_file.read())
                            await ctx.send(f"Emoji {emoji_name} added to the server!")
                        except discord.HTTPException as e:
                            await ctx.send(f"Failed to add emoji {emoji_name} to the server: {e}")
                else:
                    await ctx.send(f"Invalid emoji format for {emoji_str}.")
            else:
                await ctx.send(f"Please provide a valid custom emoji for {emoji_str}.")
                
    # Error handling for permissions
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permissions to use this command.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(EmojiManager(bot))
