import discord
from discord.ext import commands
from github import GithubIntegration
import github
import json
import os

def get_config():
    with open('../../config.json', 'r') as f:
        config = json.load(f)
    return config

class Feedback(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = get_config()
        self.github_repo = "Exohayvan/atsuko"
        self.app_id = self.config.get('APP_ID')
        self.installation_id = self.config.get('INSTALLATION_ID')
        self.private_key_path = self.config.get('PRIVATE_KEY_PATH')

    @discord.app_commands.command(name='feedback', description='Provide feedback about the bot.')
    async def feedback(self, interaction: discord.Interaction, message: str):
        """Provide feedback to bot owners, feedback will be posted to GitHub. Link to issue will be sent after feedback is posted to GitHub."""
        issue_title = f"User Feedback: {interaction.user} - {interaction.id}"
        issue_body = (f"**User Message:** {message}\n"
                      f"**Author:** {interaction.user}\n"
                      f"**Channel:** {interaction.channel}")

        private_key = open(self.private_key_path, 'r').read()
        integration = GithubIntegration(self.app_id, private_key)
        token = integration.get_access_token(self.installation_id)

        try:
            g = github.Github(token.token)
            repo = g.get_repo(self.github_repo)
            issue = repo.create_issue(title=issue_title, body=issue_body)
        
            # Add 'feedback' label after the issue is created
            label = repo.get_label("feedback")
            issue.add_to_labels(label)
        
            embed = discord.Embed(title='Feedback received', color=0x00ff00)
            embed.add_field(name='Issue created on GitHub', value=f'[Link to issue]({issue.html_url})', inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"I am unable to open an issue on GitHub.")
            await interaction.followup.send(f"An unexpected error occurred: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Feedback(bot))