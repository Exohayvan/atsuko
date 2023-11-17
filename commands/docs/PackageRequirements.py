from discord.ext import commands
import sys
import pkg_resources
import asyncio

class PackageRequirements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_requirements()

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(20)
        self.generate_requirements()

    def get_loaded_packages(self):
        """Get a set of names of loaded packages."""
        loaded_packages = set()
        for module_name in sys.modules:
            try:
                # Check if the module is a package and not an internal or built-in module
                module = sys.modules[module_name]
                if hasattr(module, '__path__') and not module.__name__.startswith('_'):
                    package = pkg_resources.get_distribution(module_name).project_name
                    loaded_packages.add(package)
            except (pkg_resources.DistributionNotFound, AttributeError):
                continue
        return loaded_packages

    def generate_requirements(self):
        """Generates or updates the requirements.txt file."""
        loaded_packages = self.get_loaded_packages()

        requirements = '\n'.join(sorted(loaded_packages))
        with open("./requirements.txt", "w") as f:
            f.write(requirements)
        print("requirements.txt has been generated/updated.")

async def setup(bot):
    await bot.add_cog(PackageRequirements(bot))
