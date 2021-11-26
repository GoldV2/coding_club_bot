from types import NoneType
from typing import Union
import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.member import Member

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {view.opponent.nick}'s turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {view.challenger.nick}'s turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'{view.challenger.nick} won!'
            elif winner == view.O:
                content = f'{view.opponent.nick} won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        old_content = interaction.message.content.split("\n")
        new_content = f"{old_content[0]}\n{content}"
        await interaction.response.edit_message(content=new_content, view=view)

class TicTacToe(discord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self, challenger: Member, opponent: Member):
        super().__init__(timeout=None)
        self.current_player = self.X
        self.challenger = challenger
        self.opponent = opponent
        self.player = {self.X: challenger, self.O: opponent}
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.player[self.current_player]:
            await interaction.response.send_message(f"It is {self.player[self.current_player].nick}'s turn.", ephemeral=True)
            return False

        else:
            return True

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self) -> Union[int, NoneType]:
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def sent_in_tic_tac_toe_channel(ctx):
        return ctx.channel.name == '❌tic-tac-toe⭕'

    @commands.command()
    @commands.check(sent_in_tic_tac_toe_channel)
    async def tic(self, ctx, opponent) -> NoneType:
        challenger = ctx.author
        opponent = ctx.guild.get_member(int(opponent[3:-1]))
        await ctx.send(f'{challenger.nick} vs. {opponent.nick}\n{challenger.nick} goes first', view=TicTacToe(challenger, opponent))

def setup(bot):
    bot.add_cog(Game(bot))