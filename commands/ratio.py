from discord.ext import commands
import random

class Ratio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ratio(self, ctx):
        """Generates a funny 'ratio' response."""
        ratios = [
            "The ratio is strong with this one!",
            "You're swimming in the ratio sauce!",
            "The ratio gods are on your side!",
            "You've achieved the perfect ratio!",
            "The ratio is going wild!",
            "Your ratio is off the charts!",
            "That's a spicy ratio!",
            "You've discovered the secret to the ultimate ratio!",
            "Prepare for ratio overload!",
            "The ratio enthusiasts are cheering for you!",
            "Your ratio game is on point!",
            "Congratulations, you've reached the ratio hall of fame!",
            "Your ratio is as majestic as a unicorn!",
            "The ratio universe is bending to your will!",
            "The ratio police have nothing on you!",
            "You've unlocked the secret ratio achievement!",
            "Brace yourself for an avalanche of ratios!",
            "Your ratio is giving everyone FOMO!",
            "The ratio monsters are trembling in fear!",
            "Your ratio is breaking all records!",
            "You're the Picasso of ratios!",
            "The ratio scientists are in awe of your discovery!",
            "Your ratio is out of this world!",
            "Behold, the mighty ruler of ratios!",
            "Your ratio is the stuff of legends!",
            "Prepare for a ratio fireworks show!",
            "You've entered the ratio zone!",
            "Your ratio is causing a sensation!",
            "The ratio empire bows down to you!",
            "Your ratio is pure gold!",
            "Witness the magic of your incredible ratio!",
            "Your ratio game is on fire!",
            "The ratio whispers your name in admiration!",
            "You've mastered the art of the perfect ratio!",
            "Your ratio is making the competition cry!",
            "The ratio deities are singing your praises!",
            "You're a ratio virtuoso!",
            "Your ratio is the envy of all!",
            "Unlocking the secrets of the ratio universe, one meme at a time!",
            "Your ratio is a work of art!",
            "The ratio legends will tell tales of your greatness!",
            "Your ratio is the eighth wonder of the world!",
            "Join the ratio revolution, led by none other than you!",
            "Your ratio is a mathematical marvel!",
            "The ratio critics have declared you a genius!",
            "You've achieved ratio enlightenment!",
            "Your ratio is a shining beacon in the meme world!",
            "Prepare to bask in the glory of your epic ratio!",
            "The ratio armies rally behind your banner!",
            "Your ratio is rewriting the laws of physics!",
            "The ratio universe bows down to your superiority!",
            "You've ascended to the highest realm of ratios!",
            "Embrace the eternal embrace of the ratio gods!",
            "Your ratio is the true meaning of perfection!"
        ]

        response = random.choice(ratios)
        await ctx.send(response)

def setup(bot):
    await bot.add_cog(Ratio(bot))
