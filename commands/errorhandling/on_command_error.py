from discord.ext import commands
import json
from github import Github
import traceback
import sys, platform

def get_config():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    print(config)
    return config

# Retrieve the GitHub token from the config file
config = get_config()
github_token = config.get('GITHUB_TOKEN')

# Use the retrieved token in your code
class ErrorHandling(commands.Cog):
    def __init__(self, bot, github_token):
        self.bot = bot
        self.github_token = github_token
        self.github_repo = "Exohayvan/atsuko"

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandError):
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            traceback_str = "".join(tb)
    
            issue_title = f"Auto Generated Report: {str(error)}"
            issue_body = (f"**User Message:** {ctx.message.content}\n"
                          f"**Error:** {str(error)}\n"
                          f"**Traceback:** ```python\n{traceback_str}```\n"
                          f"**Command:** {ctx.command.qualified_name}\n"
                          f"**Author:** {ctx.author}\n"
                          f"**Channel:** {ctx.channel}\n"
                          f"**Python Version:** {sys.version}\n"
                          f"**discord.py Version:** {discord.__version__}\n"
                          f"**OS:** {platform.system()} {platform.release()}")
    
            g = Github(self.github_token)
            repo = g.get_repo(self.github_repo)
            issue = repo.create_issue(title=issue_title, body=issue_body)
    
            embed = Embed(title='An error occurred', color=0xff0000)
            embed.add_field(name='Issue created on GitHub', value=f'[Link to issue]({issue.html_url})', inline=False)
            await ctx.send(embed=embed)
                                    
async def setup(bot):
    github_token = config.get('GITHUB_TOKEN')
    await bot.add_cog(ErrorHandling(bot, github_token))