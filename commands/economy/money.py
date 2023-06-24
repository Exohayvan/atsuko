from discord.ext import commands
import random
import sqlite3
import datetime

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
            await ctx.send(f"{member.mention} has {result[0]} gold.")
        else:
            await ctx.send(f"{member.mention} has 0 gold.")

    @commands.command()
    async def daily(self, ctx):
        """Receive your daily gold."""
        user_id = str(ctx.author.id)

        self.cursor.execute('SELECT balance, last_daily FROM UserBalance WHERE user_id=?', (user_id,))
        result = self.cursor.fetchone()
        if result and result[1] == str(datetime.date.today()):
            await ctx.send('You already received your daily gold.')
            return

        gold_gain = 0
        if random.randint(1, 100) <= 80:
            gold_gain = random.randint(50, 250)

        if result:
            self.cursor.execute('UPDATE UserBalance SET balance=balance+?, last_daily=? WHERE user_id=?', (gold_gain, str(datetime.date.today()), user_id))
        else:
            self.cursor.execute('INSERT INTO UserBalance (user_id, balance, last_daily) VALUES (?, ?, ?)', (user_id, gold_gain, str(datetime.date.today())))

        self.db.commit()
        await ctx.send(f"You received {gold_gain} gold.")

async def setup(bot):
    await bot.add_cog(Money(bot))
