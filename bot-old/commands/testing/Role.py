import discord
from discord.ext import commands
import sqlite3

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('./data/db/reactionroles.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS reaction_roles
                          (message_id INTEGER, emoji TEXT, role_id INTEGER)''')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.check_reaction_roles()

    async def check_reaction_roles(self):
        self.c.execute("SELECT DISTINCT message_id FROM reaction_roles")
        messages = self.c.fetchall()
        for (message_id,) in messages:
            try:
                channel = self.bot.get_channel(message_id)  # Adjust this if channel_id is different from message_id
                message = await channel.fetch_message(message_id)
                for reaction in message.reactions:
                    async for user in reaction.users():
                        self.c.execute("SELECT role_id FROM reaction_roles WHERE message_id=? AND emoji=?", 
                                       (message.id, str(reaction.emoji)))
                        role_id = self.c.fetchone()
                        if role_id:
                            role = message.guild.get_role(role_id[0])
                            if role:
                                if reaction.emoji in [str(r.emoji) for r in user.reactions if r.message.id == message_id]:
                                    await user.add_roles(role)
                                else:
                                    await user.remove_roles(role)
                # Re-establish the bot's awareness of these reactions
                existing_reactions = [str(reaction) for reaction in message.reactions]
                self.c.execute("SELECT emoji FROM reaction_roles WHERE message_id=?", (message_id,))
                for (emoji,) in self.c.fetchall():
                    if emoji not in existing_reactions:
                        await message.add_reaction(emoji)
            except Exception as e:
                print(f"Failed to process message {message_id}: {e}")

    @discord.app_commands.command(name="roles", description="Creates a reaction role message.")
    @discord.app_commands.describe(words="The message content", emoji_role_pairs="Emoji and role pairs in format: emoji1 role1 emoji2 role2...")
    async def create_role_message(self, interaction: discord.Interaction, words: str, emoji_role_pairs: str):
        # Processing the string of emoji_role_pairs into a list
        emoji_role_pairs = emoji_role_pairs.split()  # This requires input to be space-separated
        if len(emoji_role_pairs) % 2 != 0:
            await interaction.response.send_message("Please provide emoji and role pairs.", ephemeral=True)
            return
        
        # Send the initial message
        message = await interaction.channel.send(words)
        for i in range(0, len(emoji_role_pairs), 2):
            await message.add_reaction(emoji_role_pairs[i])
            # Assuming role ID is directly after the emoji in the list
            self.c.execute("INSERT INTO reaction_roles VALUES (?, ?, ?)", 
                           (message.id, emoji_role_pairs[i], int(emoji_role_pairs[i+1])))
        self.conn.commit()
        await interaction.response.send_message("Reaction role message created.", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        self.c.execute("SELECT role_id FROM reaction_roles WHERE message_id=? AND emoji=?", 
                       (payload.message_id, str(payload.emoji)))
        role_id = self.c.fetchone()
        if role_id:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id[0])
            if role:
                member = guild.get_member(payload.user_id)
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        self.c.execute("SELECT role_id FROM reaction_roles WHERE message_id=? AND emoji=?", 
                       (payload.message_id, str(payload.emoji)))
        role_id = self.c.fetchone()
        if role_id:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(role_id[0])
            if role:
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.c.execute("DELETE FROM reaction_roles WHERE message_id=?", (message.id,))
        self.conn.commit()

async def setup(bot):
    await bot.add_cog(Role(bot))
