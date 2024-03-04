from discord.ext import commands
import os
import asyncio
import logging

logger = logging.getLogger('DocGenerator.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/DocGenerator.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("DocGenerator Cog Loaded. Logging started...")

class DocGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_readme()

    def generate_readme(self):
        """Generates or updates the readme.md file in the current directory."""
        lines = []
        missing_details = []  # To hold missing details for each command

        logger.info("Generating README.md")
        for cog_name, cog in self.bot.cogs.items():
            logger.info(f"Processing cog: {cog_name}")
            
            # Using the get_commands() method
            commands_list = cog.get_commands()
            if not commands_list:
                logger.info(f"No commands found for cog: {cog_name}")
                continue
                
            for cmd in commands_list:
                # Skip hidden commands
                if cmd.hidden:
                    logger.info(f"Skipping hidden command: {cmd.name}")
                    continue
                # Check if help or usage is missing
                if not cmd.help:
                    missing_details.append(f"Command '{cmd.name}' in cog {cog_name} is missing help details.")
                    logger.info(f"Command '{cmd.name}' in cog {cog_name} is missing help details.")
                else:
                    lines.append(f"## {cmd.name}\n\n")
                    lines.append(f"{cmd.help}\n\n")
                    logger.info(f'Adding command "{cmd.name}" with "{cmd.help}" to readme')
                    
                if cmd.usage:
                    lines.append(f"Usage:\n`{cmd.usage}`\n\n")
                    logger.info(f'Command usage for {cmd.name} added to readme: {cmd.usage}')
                else:
                    missing_details.append(f"Command '{cmd.name}' in cog {cog_name} is missing usage details.")
                    logger.info(f'Missing command usage for {cmd.usage}')
    
        # Write to README.md
        with open("./commands/README.md", "w") as f:
            f.write(''.join(lines))
        logger.info("README.md has been generated/updated.")
    
        # Write missing details to missing.txt
        if missing_details:
            with open("missing.txt", "w") as f:
                f.write('\n'.join(missing_details))
            logger.info("missing.txt has been generated/updated.")
        else:
            # If there are no missing details and the file exists, delete it
            if os.path.exists("missing.txt"):
                os.remove("missing.txt")
                logger.info("missing.txt has been deleted as there are no missing details.")
                            
async def setup(bot):
    await bot.add_cog(DocGenerator(bot))
