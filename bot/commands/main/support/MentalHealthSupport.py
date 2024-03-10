from discord.ext import commands
import discord

class MentalHealthSupportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trigger_words = self.load_trigger_words()

    def load_trigger_words(self):
        # Initialize an empty list to store trigger words
        trigger_words = []
        # Define the path to the file
        file_path = './data/txt/mentaltriggers/english.txt'
        # Open the file and read each line
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    # Strip whitespace and add the trigger word to the list
                    trigger_word = line.strip()
                    if trigger_word:  # Ensure the line is not empty
                        trigger_words.append(trigger_word.lower())  # Add trigger word in lowercase to ensure case-insensitive matching
        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
        except Exception as e:
            print(f"An error occurred while reading {file_path}: {e}")
        return trigger_words

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if any trigger word is in the message and if the author is not the bot
        if any(word in message.content.lower() for word in self.trigger_words) and message.author != self.bot.user:
            embed = discord.Embed(
                title="It's Okay to Ask for Help",
                description=("It seems like you might be going through a tough time. If you need someone to talk to, there are people who can help. "
                             "Here are some resources and support numbers."),
                color=discord.Color.blue()
            )
            embed.add_field(name="Crisis Support Numbers", value="[Click here for resources](https://github.com/Exohayvan/atsuko/blob/main/docs/Crisis-Support-Numbers.md)", inline=False)
            embed.set_footer(text="Remember, you are not alone.")

            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MentalHealthSupportCog(bot))
