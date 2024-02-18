from discord.ext import commands
import random

class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_list = ["apple", "banana", "cherry", "orange", "kiwi"]
        self.active_game = False
        self.current_word = ""
        self.guessed_letters = []

    @commands.group(invoke_without_command=True)
    async def hangman(self, ctx):
        """Start or play a game of Hangman! Use '!hangman start' to start a new game and '!hangman guess <letter>' to make a guess."""
        pass

    @hangman.command()
    async def start(self, ctx):
        """Start a game of Hangman."""
        if self.active_game:
            await ctx.send("There's already an active game of Hangman. Finish it first!")
            return

        self.current_word = random.choice(self.word_list)
        self.guessed_letters = []
        self.active_game = True

        masked_word = "".join("_" if letter not in self.guessed_letters else letter for letter in self.current_word)
        await ctx.send(f"Let's play Hangman!\nWord: {masked_word}")

    @hangman.command()
    async def guess(self, ctx, letter: str):
        """Guess a letter in the Hangman game."""
        if not self.active_game:
            await ctx.send("There's no active game of Hangman. Start one with the '!hangman start' command.")
            return

        if len(letter) != 1 or not letter.isalpha():
            await ctx.send("Invalid guess! Please enter a single alphabetical letter.")
            return

        letter = letter.lower()

        if letter in self.guessed_letters:
            await ctx.send("You already guessed that letter. Try a different one.")
            return

        self.guessed_letters.append(letter)

        masked_word = "".join("_" if letter not in self.guessed_letters else letter for letter in self.current_word)

        if masked_word == self.current_word:
            await ctx.send(f"Congratulations! You guessed the word: {self.current_word}")
            self.active_game = False
        else:
            await ctx.send(f"Good guess!\nWord: {masked_word}")

async def setup(bot):
    await bot.add_cog(Hangman(bot))
