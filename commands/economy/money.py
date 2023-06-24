from discord.ext import commands
import random
import sqlite3
from datetime import datetime, timedelta

# Define these at the top of your script
MAX_AMT = 250
MIN_AMT = 50
ZERO_AMT_CHANCE = 20  # Chance of receiving zero gold
CURRENCY_NAME = "gold"

class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('./data/money.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserBalance (
        user_id TEXT PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        last_daily TEXT DEFAULT NULL
        )''')
        self.db.commit()

    @commands.command(aliases=['bal'])
    async def balance(self, ctx, member: commands.MemberConverter = None):
        """Check your balance or someone else's by mentioning them."""
        if member is None:
            member = ctx.author
        user_id = str(member.id)

        self.cursor.execute('SELECT balance FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()

        if result:
            await ctx.send(f"{member.mention} has {result[0]} {CURRENCY_NAME}.")
        else:
            await ctx.send(f"{member.mention} has 0 {CURRENCY_NAME}.")

    @commands.command()
    async def daily(self, ctx):
        """Receive your daily gold."""
        user_id = str(ctx.author.id)

        self.cursor.execute('SELECT balance, last_daily FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()

        if result and result[1] is not None and datetime.now() - datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S.%f") < timedelta(days=1):
            await ctx.send('You already received your daily gold. Please wait until tomorrow.')
            return

        gold_gain = random.randint(MIN_AMT, MAX_AMT) if random.randint(1, 100) > ZERO_AMT_CHANCE else 0

        if result:
            self.cursor.execute('UPDATE UserBalance SET balance=balance+?, last_daily=? WHERE user_id=?', (gold_gain, datetime.now(), user_id))
        else:
            self.cursor.execute('INSERT INTO UserBalance (user_id, balance, last_daily) VALUES (?, ?, ?)', (user_id, gold_gain, datetime.now()))

        self.db.commit()
        await ctx.send(f"You received {gold_gain} {CURRENCY_NAME}.")

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

async def setup(bot):
    await bot.add_cog(Money(bot))
