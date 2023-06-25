from discord.ext import commands

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.current_player = 'X'
        self.winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        self.game_over = False

    @commands.group(invoke_without_command=True)
    async def tictactoe(self, ctx):
        """Start or play a game of Tic-Tac-Toe! Use '!tictactoe start' to start a new game and '!tictactoe move <position>' to make a move."""
        pass

    @tictactoe.command()
    async def start(self, ctx):
        """Start a game of Tic-Tac-Toe."""
        self.board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.current_player = 'X'
        self.game_over = False

        await ctx.send("Let's play Tic-Tac-Toe!\nUse the command '!tictactoe move <position>' to make your move.\nThe board looks like this:\n" + self.get_board())

    @tictactoe.command()
    async def move(self, ctx, position: int):
        """Make a move in the Tic-Tac-Toe game."""
        if self.game_over:
            await ctx.send("The game is already over. Start a new game with the '!tictactoe start' command.")
            return

        if not 1 <= position <= 9:
            await ctx.send("Invalid position! Please choose a number between 1 and 9.")
            return

        index = position - 1

        if self.board[index] == 'X' or self.board[index] == 'O':
            await ctx.send("Invalid move! That position is already taken.")
            return

        self.board[index] = self.current_player
        await ctx.send(f"{self.current_player} placed their mark at position {position}.\n{self.get_board()}")

        if self.check_winner():
            await ctx.send(f"Congratulations! {self.current_player} wins!")
            self.game_over = True
        elif self.is_board_full():
            await ctx.send("It's a tie! The game is over.")
            self.game_over = True
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'

    def get_board(self):
        board_str = ''
        for i, mark in enumerate(self.board):
            board_str += mark + ' '
            if (i + 1) % 3 == 0:
                board_str += '\n'
        return board_str

    def check_winner(self):
        for combination in self.winning_combinations:
            a, b, c = combination
            if self.board[a] == self.board[b] == self.board[c]:
                return True
        return False

    def is_board_full(self):
        return all(mark == 'X' or mark == 'O' for mark in self.board)

async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
