from discord.ext import commands
import random
import sqlite3
from datetime import datetime, timedelta

# Define these at the top of your script
MAX_AMT = 250
MIN_AMT = 50
ZERO_AMT_CHANCE = 10  # Chance of receiving zero gold
INVEST_RETURN = 0.05  # 5% return on investment
CURRENCY_NAME = "gold"

class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('./data/db/money.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserBalance (
        user_id TEXT PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        investment INTEGER DEFAULT 0,
        last_daily TEXT DEFAULT NULL
        )''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Pot (
        pot_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 100
        )''')

        self.cursor.execute("INSERT INTO Pot (pot_id, balance) SELECT 1, 100 WHERE NOT EXISTS(SELECT 1 FROM Pot WHERE pot_id = 1)")
        self.db.commit()

    @commands.command(aliases=['bal'])
    async def balance(self, ctx, member: commands.MemberConverter = None):
        """Check your balance or someone else's by mentioning them."""
        if member is None:
            member = ctx.author
        user_id = str(member.id)
    
        self.cursor.execute('SELECT balance, investment FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
    
        if result:
            await ctx.send(f"{member.mention} has {result[0]} {CURRENCY_NAME} and {result[1]} {CURRENCY_NAME} invested.")
        else:
            await ctx.send(f"{member.mention} has 0 {CURRENCY_NAME}.")
    
    @commands.command()
    async def daily(self, ctx):
        """Receive your daily gold."""
        user_id = str(ctx.author.id)

        self.cursor.execute('SELECT balance, investment, last_daily FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()

        if result and result[2] is not None:
            time_difference = datetime.now() - datetime.strptime(result[2], "%Y-%m-%d %H:%M:%S.%f")
            if time_difference < timedelta(days=1):
                time_left = timedelta(days=1) - time_difference
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                await ctx.send(f'You already received your daily gold. Please wait {hours} hour(s) and {minutes} minute(s) to claim again.')
                return

        gold_gain = random.randint(MIN_AMT, MAX_AMT) if random.randint(1, 100) > ZERO_AMT_CHANCE else 0
        invest_gain = int(result[1] * INVEST_RETURN) if result else 0

        total_gain = int(gold_gain + invest_gain)  # Ensure total gain is an integer

        if result:
            self.cursor.execute('UPDATE UserBalance SET balance=balance+?, last_daily=? WHERE user_id=?', (total_gain, datetime.now(), user_id))
        else:
            self.cursor.execute('INSERT INTO UserBalance (user_id, balance, last_daily) VALUES (?, ?, ?)', (user_id, total_gain, datetime.now()))

        self.db.commit()
        await ctx.send(f"You received {gold_gain} {CURRENCY_NAME}.\nYour investments brought in an additional {invest_gain} {CURRENCY_NAME}!")

    @commands.command()
    async def invest(self, ctx, amount: int):
        """Invest your gold to earn more."""
        user_id = str(ctx.author.id)

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
            roll = random.randint(1, 500)
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
