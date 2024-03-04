from discord.ext import commands
from discord import Embed, Forbidden
from discord.ext.commands import CheckFailure, MissingRequiredArgument
import github
import json
import logging
import sys
import platform
import discord
import traceback
import logging

logger = logging.getLogger('CommandError.py')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/CommandError.py.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.info("CommandError Cog Loaded. Logging started...")

def get_config():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    return config

# Retrieve the private key path from the config file
config = get_config()
private_key_path = config.get('PRIVATE_KEY_PATH')

class CommandError(commands.Cog):
    def __init__(self, bot, private_key_path):
        self.bot = bot
        self.private_key_path = private_key_path
        self.github_repo = "Exohayvan/atsuko"
        self.app_id = config.get('APP_ID')
        self.installation_id = config.get('INSTALLATION_ID')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Error: commands.CheckFailure\nYou don't have the required permissions to use this command! If you believe you should have permission to use this command, please open an issue with the feedback command explaining the issue.")
            logger.info(f"commands.CheckFailure: {ctx.message.content}")
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send("Error: commands.BadArgument\nIt appears that you have used an incorrect argument. Please use `!help <command>` to see correct usage. If you still run into an issue, please use `!feedback <describe issue>` to report.")
            logger.info(f"commands.BadArgument: {ctx.message.content}")
            return
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Error: commands.MissingRequiredArgument\nIt appears thats you are missing a required argument. Please use `!help <command>` to see correct usage. If you still run into an issue, please use `!feedback <describe issue>` to report.")
            logger.info(f"commands.MissingRequiredArgument: {ctx.message.content}")
            return
        error_message = str(error.original) if hasattr(error, 'original') else str(error)
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        traceback_str = "".join(tb).strip()

        issue_title = f"Auto Generated Report: {error_message}"
        issue_body = (f"**User Message:** {ctx.message.content}\n"
                      f"**Error:** {error_message}\n"
                      f"**Traceback:** \n```python\n{traceback_str}\n```\n"
                      f"**Command:** `{ctx.command.qualified_name}`\n"
                      f"**Author:** {ctx.author}\n"
                      f"**Channel:** {ctx.channel}\n"
                      f"**Python Version:** `{sys.version}`\n"
                      f"**discord.py Version:** `{discord.__version__}`\n"
                      f"**OS:** `{platform.system()} {platform.release()}`")

        # Use GithubIntegration for app authentication
        private_key = open(self.private_key_path, 'r').read()
        integration = github.GithubIntegration(self.app_id, private_key)
        token = integration.get_access_token(self.installation_id)

        try:
            g = github.Github(token.token)
            repo = g.get_repo(self.github_repo)
            issue = repo.create_issue(title=issue_title, body=issue_body)
            bug_label = repo.get_label("bug")
            issue.add_to_labels(bug_label)

            embed = Embed(title='An error occurred', color=0xff0000)
            embed.add_field(name='Issue created on GitHub', value=f'[Link to issue]({issue.html_url})', inline=False)
            await ctx.send(embed=embed)
            logger.info(f"New issue opened on GitHub: {issue.html_url}")
        except Exception as e:
            await ctx.send(f"I am unable to open an issue on GitHub.")
            await ctx.send(f"An unexpected error occurred: {e}")
            logger.info(f"Unable to open an issue: {e}")

async def setup(bot):
    config = get_config()
    private_key_path = config.get('PRIVATE_KEY_PATH')
    await bot.add_cog(CommandError(bot, private_key_path))