from discord.ext import commands
import json
from github import GithubIntegration
import Github
import traceback
import sys, platform
import discord
from discord import Embed
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        self.app_id = config.get('APP_ID')  # You should store your app id in the config file
        self.installation_id = config.get('INSTALLATION_ID')  # You should store your installation id in the config file

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandError):
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            traceback_str = "".join(tb).strip()  # remove leading/trailing white spaces
    
            issue_title = f"Auto Generated Report: {str(error)}"
            issue_body = (f"**User Message:** {ctx.message.content}\n"
                  f"**Error:** {str(error)}\n"
                  f"**Traceback:** \n```python\n{traceback_str}\n```\n"  # extra newline here
                  f"**Command:** `{ctx.command.qualified_name}`\n"  # use inline code format for single line code
                  f"**Author:** {ctx.author}\n"
                  f"**Channel:** {ctx.channel}\n"
                  f"**Python Version:** `{sys.version}`\n"  # use inline code format for single line code
                  f"**discord.py Version:** `{discord.__version__}`\n"  # use inline code format for single line code
                  f"**OS:** `{platform.system()} {platform.release()}`")  # use inline code format for single line code

            # Use GithubIntegration for app authentication
            private_key = open(self.private_key_path, 'r').read()
            integration = GithubIntegration(self.app_id, private_key)
            token = integration.get_access_token(self.installation_id)

            try:
                g = Github(token.token)
                repo = g.get_repo(self.github_repo)
                issue = repo.create_issue(title=issue_title, body=issue_body)
                embed = Embed(title='An error occurred', color=0xff0000)
                embed.add_field(name='Issue created on GitHub', value=f'[Link to issue]({issue.html_url})', inline=False)
                await ctx.send(embed=embed)
            except Exception as e:
                logger.exception("Failed to create GitHub issue")    

async def setup(bot):
    config = get_config()
    private_key_path = config.get('PRIVATE_KEY_PATH')
    await bot.add_cog(CommandError(bot, private_key_path))
    