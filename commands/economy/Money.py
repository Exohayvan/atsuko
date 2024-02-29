from discord.ext import commands
from discord import app_commands
import discord
import random
import sqlite3
from datetime import datetime, timedelta
import asyncio

# Define these at the top of your script
MAX_AMT = 250
MIN_AMT = 50
ZERO_AMT_CHANCE = 10  # Chance of receiving zero gold
INVEST_RETURN = 0.05  # 5% return on investment
CURRENCY_NAME = "gold"

class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_databases()

        # Start the background task
        self.bot.loop.create_task(self.daily_reminder_check())

    def init_databases(self):
        try:
            # Initialize the money database
            self.db = sqlite3.connect('./data/db/money.db')
            self.cursor = self.db.cursor()
            self.init_money_db_tables()

            # Initialize the reminder database
            self.remind_db = sqlite3.connect('./data/db/dailyremind.db')
            self.remind_cursor = self.remind_db.cursor()
            self.init_remind_db_tables()
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to databases: {e}")

    def init_money_db_tables(self):
        try:
            # Your money.db table creation queries go here
            self.cursor.execute("CREATE TABLE IF NOT EXISTS UserBalance ...")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Pot ...")
            self.cursor.execute("INSERT INTO Pot ...")
            self.db.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while initializing money.db tables: {e}")

    def init_remind_db_tables(self):
        try:
            # Create DailyRemind table with all necessary columns
            self.remind_cursor.execute("""
                CREATE TABLE IF NOT EXISTS DailyRemind (
                    user_id TEXT PRIMARY KEY,
                    last_channel_id TEXT,
                    reminded_today BOOLEAN DEFAULT FALSE
                )
            """)
            self.remind_db.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while initializing dailyremind.db tables: {e}")
        
    @discord.app_commands.command(name="dailyremind", description="Toggle daily reminders on or off.")
    @discord.app_commands.describe(status="Specify 'on' to enable or 'off' to disable daily reminders.")
    async def dailyremind(self, interaction: discord.Interaction, status: str):
        """Toggle daily reminders on or off."""
        user_id = str(interaction.user.id)
        last_channel_id = str(interaction.channel_id)
        if option.lower() in ['on', 'true']:
            self.remind_cursor.execute('REPLACE INTO DailyRemind (user_id, last_channel_id) VALUES (?, ?)', (user_id, last_channel_id))
            await interaction.response.send_message("Daily reminders turned on.")
        elif option.lower() in ['off', 'false']:
            self.remind_cursor.execute('DELETE FROM DailyRemind WHERE user_id=?', (user_id,))
            await interaction.response.send_message("Daily reminders turned off.")
        else:
            await interaction.response.send_message("Invalid option. Please use 'on' or 'off'.")
        self.remind_db.commit()

    async def daily_reminder_check(self):
        while True:
            await asyncio.sleep(60)  # Wait for 60 seconds between each check
            current_time = datetime.now()
            if current_time.hour == 0 and current_time.minute <= 1:  # Reset reminders once a day
                self.remind_cursor.execute('UPDATE DailyRemind SET reminded_today = FALSE')
                self.remind_db.commit()

            self.remind_cursor.execute('SELECT user_id, last_channel_id FROM DailyRemind WHERE reminded_today = FALSE')
            users_to_remind = self.remind_cursor.fetchall()
            for user_id, last_channel_id in users_to_remind:
                self.cursor.execute('SELECT last_daily FROM UserBalance WHERE user_id=?', (user_id,))
                result = self.cursor.fetchone()
                if result and result[0]:
                    time_difference = datetime.now() - datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f")
                    if time_difference >= timedelta(days=1):
                        channel = self.bot.get_channel(int(last_channel_id))
                        if channel:
                            await channel.send(f'<@{user_id}> you can claim your daily again!')
                            self.remind_cursor.execute('UPDATE DailyRemind SET reminded_today = TRUE WHERE user_id = ?', (user_id,))
                            self.remind_db.commit()
                            
    @app_commands.command(name="balance", description="Check your balance or someone else's by mentioning them.")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        """Check your balance or someone else's by mentioning them."""
        if member is None:
            member = interaction.user
        user_id = str(member.id)
        
        self.cursor.execute('SELECT balance, investment FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
        total_bal = result[0] + result[1]
        
        if result:
            total_bal = result[0] + result[1]
            currency_name = "Gold"  # Replace "Gold" with your currency name
            await interaction.response.send_message(f"{member.mention} has **{total_bal} {currency_name}**! \n*({result[0]} {currency_name} in their pocket and {result[1]} {currency_name} invested.)*")
        else:
            await interaction.response.send_message(f"{member.mention} has 0 {currency_name}.")
    
    @app_commands.command(name="daily", description="Receive your daily gold.")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        self.cursor.execute('SELECT balance, investment, last_daily FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()

        if result and result[2] is not None:
            time_difference = datetime.now() - datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S.%f")
            if time_difference < timedelta(days=1):
                time_left = timedelta(days=1) - time_difference
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await interaction.response.send_message(f'You already received your daily gold. Please wait {hours} hour(s) and {minutes} minute(s) to claim again.')
                return

        gold_gain = random.randint(MIN_AMT, MAX_AMT) if random.randint(1, 100) > ZERO_AMT_CHANCE else 0
        invest_gain = int(result[1] * INVEST_RETURN) if result else 0

        total_gain = int(gold_gain + invest_gain)  # Ensure total gain is an integer

        if result:
            self.cursor.execute('UPDATE UserBalance SET balance=balance+?, last_daily=? WHERE user_id=?', (total_gain, datetime.now(), user_id))
            
        else:
            self.cursor.execute('INSERT INTO UserBalance (user_id, balance, last_daily) VALUES (?, ?, ?)', (user_id, total_gain, datetime.now()))
            
        # Reset the reminded_today flag to False after claiming the daily gold
        self.remind_cursor.execute('UPDATE DailyRemind SET reminded_today = FALSE WHERE user_id = ?', (user_id,))
        self.remind_db.commit()
        self.db.commit()
        await interaction.response.send_message(f"You received {gold_gain} {CURRENCY_NAME}.\nYour investments brought in an additional {invest_gain} {CURRENCY_NAME}!")

    @commands.command()
    async def invest(self, ctx, amount: str):
        """Invest your gold to earn more."""
        user_id = str(ctx.author.id)
    
        # Check if the input can be converted to an integer
        if not amount.isdigit():
            await ctx.send("Please enter a valid integer for the amount.")
            return
    
        # Convert the amount to an integer
        amount = int(amount)

        # Check if the user has enough gold to invest
        self.cursor.execute('SELECT balance FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
        if result is None or result[0] < amount:
            await ctx.send("You don't have enough gold to invest.")
            return

        # Subtract gold from the balance and add to investment
        self.cursor.execute('UPDATE UserBalance SET balance=balance-?, investment=investment+? WHERE user_id=?', (amount, amount, user_id))
        self.db.commit()

        await ctx.send(f"You invested {amount} {CURRENCY_NAME}.")

    @commands.command()
    async def uninvest(self, ctx, amount: int):
        """Uninvest your gold, with a 10% penalty."""
        user_id = str(ctx.author.id)
    
        # Check if the user has enough gold invested
        self.cursor.execute('SELECT investment FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
        if result is None or result[0] < amount:
            await ctx.send("You don't have enough gold invested to withdraw.")
            return
    
        # Subtract gold from the investment and add 90% to balance
        penalty = int(amount * 0.1)  # 10% penalty
        return_amount = int(amount - penalty)  # Amount returned to balance (ensure it's integer by rounding down)
        self.cursor.execute('UPDATE UserBalance SET balance=balance+?, investment=investment-? WHERE user_id=?', (return_amount, amount, user_id))
        self.db.commit()
    
        await ctx.send(f"You uninvested {amount} {CURRENCY_NAME}. You received {return_amount} {CURRENCY_NAME} back after a 10% penalty.")
    
    @commands.command()
    async def give(self, ctx, member: commands.MemberConverter, amount: int):
        """Give gold to someone."""
        user_id = str(ctx.author.id)
        target_id = str(member.id)

        # Check if the user has enough gold to give
        self.cursor.execute('SELECT balance FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
        if result is None or result[0] < amount:
            await ctx.send("You don't have enough gold to give.")
            return

        # Subtract gold from the giver
        self.cursor.execute('UPDATE UserBalance SET balance=balance-? WHERE user_id=?', (amount, user_id))

        # Add gold to the receiver
        self.cursor.execute('SELECT balance FROM UserBalance WHERE user_id=?', (target_id,))
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute('UPDATE UserBalance SET balance=balance+? WHERE user_id=?', (amount, target_id))
        else:
            self.cursor.execute('INSERT INTO UserBalance (user_id, balance) VALUES (?, ?)', (target_id, amount))

        self.db.commit()
        await ctx.send(f"You gave {amount} {CURRENCY_NAME} to {member.mention}.")

    @commands.command()
    async def gamble(self, ctx, amount: int):
        """Gamble your gold for a chance to win the pot."""
        user_id = str(ctx.author.id)
        # Initialize pot_balance with the current balance from the Pot table
        self.cursor.execute('SELECT balance FROM Pot WHERE pot_id=1')
        pot_balance = self.cursor.fetchone()[0]
        
        # Check if the user has enough gold to gamble
        self.cursor.execute('SELECT balance FROM UserBalance WHERE user_id=?', (user_id,))
        user_balance = self.cursor.fetchone()
        if user_balance is None or user_balance[0] < amount:
            await ctx.send("You don't have enough gold to gamble.")
            return

        # Start rolling
        await ctx.send("Starting roll...")
        rolled = 0
        for _ in range(amount):
            roll = random.randint(1, 50000)
            if roll <= 1:  # Win
                self.cursor.execute('SELECT balance FROM Pot WHERE pot_id=1')
                pot_balance = self.cursor.fetchone()[0]
                win_balance = (pot_balance - rolled)
                self.cursor.execute('UPDATE UserBalance SET balance=balance+? WHERE user_id=?', (pot_balance, user_id))
                self.cursor.execute('UPDATE Pot SET balance=100 WHERE pot_id=1')
                self.db.commit()

                await ctx.send(f"You won the pot of {win_balance} {CURRENCY_NAME}!\n(It only took {rolled} rolls)")
                return  # Return after winning
            rolled += 1
            # If not a win, take bet from balance and add to pot
            self.cursor.execute('UPDATE UserBalance SET balance=balance-1 WHERE user_id=?', (user_id,))
            self.cursor.execute('UPDATE Pot SET balance=balance+1 WHERE pot_id=1')
        self.db.commit()
        await ctx.send(f"All Rolls finished. You didn't win the pot, new pot balance is {pot_balance} {CURRENCY_NAME}!")
        
    @commands.command(aliases=['pot'])
    async def jackpot(self, ctx):
        """Check the current jackpot amount."""
        self.cursor.execute('SELECT balance FROM Pot WHERE pot_id=1')
        pot_balance = self.cursor.fetchone()[0]
        await ctx.send(f"The current jackpot is {pot_balance} {CURRENCY_NAME}.")

async def setup(bot):
    await bot.add_cog(Money(bot))
