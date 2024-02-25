from discord.ext import commands
import subprocess
import asyncio
import logging
import aiofiles

logger = logging.getLogger('DocGenerator.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/DocGenerator.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.propagate = False
logger.info("DocGenerator Cog Loaded. Logging started...")

class PackageRequirements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.generate_requirements())

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(20)
        await self.generate_requirements()

    async def generate_requirements_with_pipreqs(self):
        """Generates or updates the requirements.txt file using pipreqs and adds pipreqs to the list."""
        # Define the command to run pipreqs
        command = ["pipreqs", ".", "--force"]
        
        # Run the command in an asynchronous manner
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        
        # Wait for the command to complete
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info("requirements.txt has been generated/updated successfully.")
            # Append pipreqs to the requirements.txt file
            async with aiofiles.open("requirements.txt", "a") as f:
                await f.write("\npipreqs\n")
        else:
            # Output the error if pipreqs failed
            logger.error(f"Failed to generate requirements.txt: {stderr.decode()}")

    async def generate_requirements(self):
        await self.generate_requirements_with_pipreqs()

async def setup(bot):
    await bot.add_cog(PackageRequirements(bot))
