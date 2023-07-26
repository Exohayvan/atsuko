from discord.ext import commands

class Donation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of dictionaries to store donation information
        self.donation_methods = [
            {'name': 'Bitcoin', 'short': 'btc', 'address': 'Your BTC address here'},
            {'name': 'Ethereum', 'short': 'eth', 'address': 'Your Ethereum address here'},
            # Add more methods and addresses by appending more dictionaries
        ]

    @commands.command(usage="!donate <method>")
    async def donate(self, ctx, method: str = None):
        """
        Returns the donation address for the specified method.
        """
        if method is None:
            await ctx.send("Please specify a donation method. Example: `!donate btc`")
            return

        # Convert method to lowercase to ensure consistency
        method = method.lower()

        # Search for the method in the list of dictionaries
        for donation_method in self.donation_methods:
            if donation_method['name'].lower() == method or donation_method['short'] == method:
                await ctx.send(f"To donate using {donation_method['name']}, send to this address: {donation_method['address']}")
                return

        await ctx.send(f"We don't support {method} currently. Please check available methods or contact an admin.")

async def setup(bot):
    await bot.add_cog(Donation(bot))
