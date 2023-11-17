from discord.ext import commands
import sys
import pkg_resources
import asyncio
import aiofiles

class PackageRequirements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.generate_requirements())

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(20)
        await self.generate_requirements()

    async def get_loaded_packages(self):
        """Get a set of names of loaded packages."""
        loop = asyncio.get_running_loop()
        loaded_packages = set()
        module_names = list(sys.modules)  # Create a static list of module names

        for module_name in module_names:
            try:
                module = sys.modules.get(module_name)
                if module and hasattr(module, '__path__') and not module.__name__.startswith('_'):
                    # Run the blocking operation in an executor
                    package = await loop.run_in_executor(None, lambda: pkg_resources.get_distribution(module_name).project_name)
                    loaded_packages.add(package)
            except (pkg_resources.DistributionNotFound, AttributeError):
                continue
        return loaded_packages

    async def generate_requirements(self):
        """Generates or updates the requirements.txt file."""
        loaded_packages = await self.get_loaded_packages()

        requirements = '\n'.join(sorted(loaded_packages))
        async with aiofiles.open("./requirements.txt", "w") as f:
            await f.write(requirements)
        print("requirements.txt has been generated/updated.")

async def setup(bot):
    await bot.add_cog(PackageRequirements(bot))
