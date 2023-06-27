from discord.ext import commands
import json
from github import Github

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
        if isinstance(error, commands.CommandError):
            issue_title = f"Error Report: {str(error)}"
            issue_body = f"**User Message:** {ctx.message.content}\n\n**Error:** {str(error)}"
    
            print(f"Token (first 4 characters): {self.github_token[:4]}")
            print(f"Repository: {self.github_repo}")
    
            g = Github(self.github_token)
            repo = g.get_repo(self.github_repo)
            repo.create_issue(title=issue_title, body=issue_body)
    
            await ctx.send(f'An error occurred. The issue has been created on GitHub.')
        
async def setup(bot):
    github_token = config.get('GITHUB_TOKEN')
    await bot.add_cog(ErrorHandling(bot, github_token))