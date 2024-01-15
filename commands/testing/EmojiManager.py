from discord.ext import commands
import os
import discord

class EmojiManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_folder = './data/emojis/'

    @commands.command(usage="!emoji_save <emoji>")
    @commands.has_permissions(manage_guild=True)
    async def emoji_save(self, ctx, emoji: discord.PartialEmoji):
        """Saves an emoji to the local storage."""
        if not os.path.exists(self.emoji_folder):
            os.makedirs(self.emoji_folder)

        emoji_filename = f"{emoji.name}.gif" if emoji.animated else f"{emoji.name}.png"
        file_path = os.path.join(self.emoji_folder, emoji_filename)

        if not os.path.exists(file_path):
            await emoji.url.save(file_path)
            await ctx.send(f"Emoji {emoji.name} saved!")
        else:
            await ctx.send("This emoji is already saved.")

    @commands.command(usage="!emoji_add <emoji>")
    @commands.has_permissions(manage_guild=True)
    async def emoji_add(self, ctx, emoji: discord.PartialEmoji):
        """Saves an emoji to local storage and adds it to the server."""
        await self.emoji_save(ctx, emoji)

        with open(os.path.join(self.emoji_folder, f"{emoji.name}.{'gif' if emoji.animated else 'png'}"), 'rb') as emoji_file:
            try:
                await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji_file.read())
                await ctx.send(f"Emoji {emoji.name} added to the server!")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to add emoji to the server: {e}")

    # Error handling for permissions
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permissions to use this command.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(EmojiManager(bot))
