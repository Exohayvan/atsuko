from discord.ext import commands
import os
import asyncio

class DocGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_readme()

    @commands.Cog.listener()
    async def on_ready(self):
        """Listener for when the bot has connected to Discord."""
        await asyncio.sleep(20)
        self.generate_readme()

    def generate_readme(self):
        """Generates or updates the readme.md file in the current directory."""
        lines = []
        missing_details = []  # To hold missing details for each command
    
        for cog_name, cog in self.bot.cogs.items():
            print(f"Processing cog: {cog_name}")  # Debugging print
            
            # Using the get_commands() method
            commands_list = cog.get_commands()
            if not commands_list:
                print(f"No commands found for cog: {cog_name}")
                continue
                
            for cmd in commands_list:
                # Check if help or usage is missing
                if not cmd.help:
                    missing_details.append(f"Command '{cmd.name}' in cog {cog_name} is missing help details.")
                else:
                    lines.append(f"## {cmd.name}\n\n")
                    lines.append(f"{cmd.help}\n\n")
                    
                if cmd.usage:
                    lines.append(f"Usage:\n`{cmd.usage}`\n\n")
                else:
                    missing_details.append(f"Command '{cmd.name}' in cog {cog_name} is missing usage details.")
    
        # Write to README.md
        with open("./commands/README.md", "w") as f:
            f.write(''.join(lines))
        print("README.md has been generated/updated.")
    
        # Write missing details to missing.txt
        if missing_details:
            with open("missing.txt", "w") as f:
                f.write('\n'.join(missing_details))
            print("missing.txt has been generated/updated.")
                            
async def setup(bot):
    await bot.add_cog(DocGenerator(bot))
