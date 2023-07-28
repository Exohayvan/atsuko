from discord.ext import commands

DISABLED_COMMANDS = set()  # We'll store disabled command names here

class CommandToggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="!disable <command_name>")
    async def disable(self, ctx, command_name: str):
        """Disable a specific command."""
        if ctx.author.id == 276782057412362241:
            if command_name in self.bot.all_commands:
                DISABLED_COMMANDS.add(command_name)
                await ctx.send(f"`{command_name}` has been disabled!")
            else:
                await ctx.send(f"No command named `{command_name}` found!")
        else:
            await ctx.send("You do not have permission to use this command!")

    @commands.command(usage="!enable <command_name>")
    async def enable(self, ctx, command_name: str):
        """Enable a previously disabled command."""
        if ctx.author.id == 276782057412362241:
            if command_name in DISABLED_COMMANDS:
                DISABLED_COMMANDS.remove(command_name)
                await ctx.send(f"`{command_name}` has been enabled!")
            else:
                await ctx.send(f"`{command_name}` is not disabled!")
        else:
            await ctx.send("You do not have permission to use this command!")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.command.name in DISABLED_COMMANDS and not ctx.author.id == 276782057412362241:
            await ctx.send(f"`{ctx.command.name}` is currently disabled!")
            ctx.command = None  # This will prevent the command from being processed further

async def setup(bot):
    await bot.add_cog(CommandToggle(bot))
