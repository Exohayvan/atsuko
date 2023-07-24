from discord.ext import commands
import os

class DocGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_readme()

    @commands.Cog.listener()
    async def on_ready(self):
        """Listener for when the bot has connected to Discord."""
        self.generate_readme()

    def generate_readme(self):
        """Generates or updates the readme.md file in the current directory."""
        lines = []
        for cog in self.bot.cogs.values():
            if hasattr(cog, "get_commands"):
                for cmd in cog.get_commands():
                    lines.append(f"## {cmd.name}\n\n")
                    lines.append(f"{cmd.help}\n\n")
                    if cmd.usage:
                        lines.append(f"**Usage:**\n\n`{cmd.usage}`\n\n")
    
        with open("./commands/README.md", "w") as f:
            f.write(''.join(lines))
    
        print("README.md has been generated/updated.")
        
async def setup(bot):
    await bot.add_cog(DocGenerator(bot))
