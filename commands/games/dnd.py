from discord.ext import commands

class Character:
    def __init__(self, name, race, character_class, gender, outfit_type, hair_color, eye_color, weapon_type, level):
        self.name = name
        self.race = race
        self.character_class = character_class
        self.gender = gender
        self.outfit_type = outfit_type
        self.hair_color = hair_color
        self.eye_color = eye_color
        self.weapon_type = weapon_type
        self.level = level

    def __str__(self):
        return f"Name: {self.name}\nRace: {self.race}\nClass: {self.character_class}\nGender: {self.gender}\nOutfit Type: {self.outfit_type}\nHair Color: {self.hair_color}\nEye Color: {self.eye_color}\nWeapon Type: {self.weapon_type}\nLevel: {self.level}"

class DND(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.characters = {}

    @commands.group(invoke_without_command=True)
    async def dnd(self, ctx):
        await ctx.send('D&D command group. Use !dnd create to create a character or !dnd show to show your character.')

    @dnd.command()
    async def create(self, ctx):
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

        await ctx.send("What is the gender of your character?")
        gender_msg = await self.bot.wait_for('message', check=check)
        gender = gender_msg.content

        await ctx.send("What is the outfit type of your character?")
        outfit_msg = await self.bot.wait_for('message', check=check)
        outfit_type = outfit_msg.content

        await ctx.send("What is the hair color of your character?")
        hair_color_msg = await self.bot.wait_for('message', check=check)
        hair_color = hair_color_msg.content

        await ctx.send("What is the eye color of your character?")
        eye_color_msg = await self.bot.wait_for('message', check=check)
        eye_color = eye_color_msg.content

        await ctx.send("What is the weapon type of your character?")
        weapon_type_msg = await self.bot.wait_for('message', check=check)
        weapon_type = weapon_type_msg.content

        await ctx.send("Your Character Will start at level 1!")
        level = 1

        character = Character(name, race, character_class, gender, outfit_type, hair_color, eye_color, weapon_type, level)
        await ctx.send(f"This is your character's details:\n{character}\nType 'confirm' to create this character.")

        confirm_msg = await self.bot.wait_for('message', check=check)
        if confirm_msg.content.lower() == 'confirm':
            self.characters[user_id] = character
            await ctx.send(f"Character '{name}' created for user {ctx.author.mention}!")
            image_generator_cog = self.bot.get_cog("ImageGenerator")
            if image_generator_cog:
                prompt = f"{race} race, {character_class} class, {gender}, {outfit_type}, {hair_color} hair, {eye_color} eyes, {weapon_type}"
                await image_generator_cog.dnddiff.invoke(ctx, prompt=prompt)
        else:
            await ctx.send("Character creation cancelled.")
            
    @dnd.command()
    async def show(self, ctx):
        """Displays the character of the user."""
        user_id = ctx.author.id
        character = self.characters.get(user_id)
        if character:
            await ctx.send(f"User {ctx.author.mention}'s character:\n{character}")
        else:
            await ctx.send("You haven't created a character yet!")

async def setup(bot):
    await bot.add_cog(DND(bot))