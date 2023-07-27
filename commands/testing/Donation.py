from discord.ext import commands

class Donation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of dictionaries to store donation information
        self.donation_methods = [
            {'name': 'Bitcoin', 'short': 'btc', 'address': '```bc1qh08qv8j0whkc8shmnr7edpvyuluza78tjtlg4j```'},
            {'name': 'Ethereum', 'short': 'eth', 'address': '```0x7c2AD5056E9191A837A8e0Be3998b37e82bF65d8```'},
            {'name': 'Binance', 'short': 'bnb', 'address': '```bnb1q4uludcq8ry55ryc9vmz6cfq4n0yvuvv725ydd```'},
            {'name': 'Binance Smart', 'short': 'bsc', 'address': '```0x7c2AD5056E9191A837A8e0Be3998b37e82bF65d8```'},
            {'name': 'Doge', 'short': 'doge', 'address': '```D9i93M1juvHBieZfbVXvxLyXGQ4yhjdfyu```'},
            {'name': 'Dash', 'short': 'dash', 'address': '```XiUV5XMKNMicSHrRduMb83131TNkgQTfsa```'},
            {'name': 'Tether', 'short': 'usdt', 'address': '```0x7c2AD5056E9191A837A8e0Be3998b37e82bF65d8 (ECR20)```'},
            {'name': 'Tether', 'short': 'usdt', 'address': '```TYpf1tVuz9XAseufTz72zfk7UTV1YpnPXv (TRX20)```'},
            {'name': 'Tether', 'short': 'usdt', 'address': '```0x7c2AD5056E9191A837A8e0Be3998b37e82bF65d8 (BEP20)```'},
            {'name': 'Tether', 'short': 'usdt', 'address': '```0x7c2AD5056E9191A837A8e0Be3998b37e82bF65d8 (Polygon)```'},

        ]

    @commands.command(usage="!donate <method>")
    async def donate(self, ctx, method: str = None):
        """
        Returns the donation address for the specified method.
        """
        if method is None:
            methods_available = [donation['short'] for donation in self.donation_methods]
            # Remove duplicates by converting to set and then back to list
            methods_available = list(set(methods_available))
            await ctx.send(f"Available donation methods:\n `{', '.join(methods_available)}.`\n Use `!donate <method>` to get the address for a specific method.")
            return
    
        # Convert method to lowercase to ensure consistency
        method = method.lower()
        addresses_found = []
    
        # Search for the method in the list of dictionaries
        for donation_method in self.donation_methods:
            if donation_method['name'].lower() == method or donation_method['short'] == method:
                addresses_found.append(donation_method['address'])
    
        if addresses_found:
            await ctx.send(f"To donate using {method}, send to one of these addresses: {''.join(addresses_found)}")
        else:
            await ctx.send(f"We don't support {method} currently. Please check available methods or contact an admin.")
                
async def setup(bot):
    await bot.add_cog(Donation(bot))
