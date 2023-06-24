import chess
import chess.svg
from discord.ext import commands

class Chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.group(invoke_without_command=True)
    async def chess(self, ctx):
        """Main chess command."""
        await ctx.send("Use '!chess start' to start a new game or '!chess move [move]' to make a move.")

    @chess.command()
    async def start(self, ctx):
        """Starts a new chess game."""
        if ctx.channel.id in self.games:
            await ctx.send("A game is already in progress in this channel.")
            return

        game = chess.Board()
        self.games[ctx.channel.id] = game

        await ctx.send("A new chess game has started. Use '!chess move [move]' to play.")

    @chess.command()
    async def move(self, ctx, move: str):
        """Makes a move in the current chess game."""
        if ctx.channel.id not in self.games:
            await ctx.send("No game in progress. Start a new game with '!chess start'.")
            return

        game = self.games[ctx.channel.id]
        try:
            chess.Move.from_uci(move)  # Validate the move format
        except ValueError:
            await ctx.send("Invalid move format. Use '!chess move [move]' with a valid move in UCI format (e.g., e2e4).")
            return

        if chess.Move.from_uci(move) not in game.legal_moves:
            await ctx.send("Invalid move. Make sure it is a legal move in the current game position.")
            return

        game.push_uci(move)

        if game.is_game_over():
            result = ""
            if game.is_checkmate():
                result = "Checkmate!"
            elif game.is_stalemate():
                result = "Stalemate!"
            elif game.is_insufficient_material():
                result = "Insufficient material!"
            elif game.is_seventyfive_moves() or game.is_fivefold_repetition() or game.is_variant_draw():
                result = "Draw!"

            await ctx.send(f"Game over. {result}")
            del self.games[ctx.channel.id]
        else:
            await ctx.send(f"Move played: {move}\n{self.get_board_svg(game)}")

    def get_board_svg(self, game):
        return chess.svg.board(board=game)

async def setup(bot):
    await bot.add_cog(Chess(bot))