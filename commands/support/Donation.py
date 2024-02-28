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

    @discord.app_commands.command(name="donate", description="Returns the donation address for the specified method.")
        async def donate(self, interaction: discord.Interaction, method: str):
            """
            Returns the donation address for the specified method.
            """
            method = method.lower()
            addresses_found = [dm['address'] for dm in self.donation_methods if dm['name'].lower() == method or dm['short'] == method]
    
            if addresses_found:
                await interaction.response.send_message(f"To donate using {method}, send to this address: {', '.join(addresses_found)}")
            else:
                methods_available = list(set(dm['short'] for dm in self.donation_methods))
                await interaction.response.send_message(f"We don't support {method} currently. Available methods: {', '.join(methods_available)}")
                            
async def setup(bot):
    await bot.add_cog(Donation(bot))
