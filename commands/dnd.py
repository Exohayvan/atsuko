from discord.ext import commands

class Character:
    def __init__(self, name, race, character_class, level):
        self.name = name
        self.race = race
        self.character_class = character_class
        self.level = level

    def __str__(self):
        return f"Name: {self.name}\nRace: {self.race}\nClass: {self.character_class}\nLevel: {self.level}"

class DND(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = {}

    @commands.command()
    async def create_character(self, ctx):
        """Creates a D&D character for the user."""
        user_id = ctx.author.id
        if user_id in self.characters:
            await ctx.send("You already have a character!")
            return

        await ctx.send("Let's create your D&D character! Answer the following questions:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("What is the name of your character?")
        name_msg = await self.bot.wait_for('message', check=check)
        name = name_msg.content

        await ctx.send("What is the race of your character?")
        race_msg = await self.bot.wait_for('message', check=check)
        race = race_msg.content

        await ctx.send("What is the class of your character?")
        class_msg = await self.bot.wait_for('message', check=check)
        character_class = class_msg.content

        await ctx.send("Your Character Will start at level 1!")
        level = 1
        
        character = Character(name, race, character_class, level)
        self.characters[user_id] = character
        await ctx.send(f"Character '{name}' created for user {ctx.author.mention}!")

    @commands.command()
    async def show_character(self, ctx):
        """Displays the character of the user."""
        user_id = ctx.author.id
        character = self.characters.get(user_id)
        if character:
            await ctx.send(f"User {ctx.author.mention}'s character:\n{character}")
        else:
            await ctx.send("You haven't created a character yet!")

async def setup(bot):
    await bot.add_cog(DND(bot))
