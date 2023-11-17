from discord.ext import commands
import os
import pkgutil
import importlib.util
import stdlib_list
import asyncio

class PackageRequirements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generate_requirements()

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(20)
        self.generate_requirements()

    def get_imports(self, path):
        imports = set()
        for root, _, files in os.walk(path):
            for file in [f for f in files if f.endswith('.py')]:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('import ') or ' import ' in line:
                            parts = line.split()
                            if 'import' in parts:
                                idx = parts.index('import')
                                module_name = parts[idx + 1].split('.')[0]
                                imports.add(module_name)
        return imports

    def get_package_name(self, module_name):
        if module_name in stdlib_list.stdlib_list("3.8"):  # Replace "3.8" with your Python version
            return None  # Skip standard library modules
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            top_level = spec.origin.split(os.sep)[0]
            if top_level in os.listdir('.'):
                return None  # Skip local packages or modules
            return spec.name.split('.')[0]  # Get the top-level package name
        return None

    def generate_requirements(self):
        bot_path = os.path.dirname(os.path.abspath(__file__))
        imported_modules = self.get_imports(bot_path)

        packages = set()
        for module in imported_modules:
            package = self.get_package_name(module)
            if package:
                packages.add(package)

        requirements = '\n'.join(sorted(packages))
        with open("./requirements.txt", "w") as f:
            f.write(requirements)
        print("requirements.txt has been generated/updated.")

async def setup(bot):
    await bot.add_cog(PackageRequirements(bot))
