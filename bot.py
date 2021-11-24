import os
import sys

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), owner_id=250782339758555136,
                   intents=Intents.all())

path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.insert(1, path)

if __name__ == "__main__":
    for file in os.listdir(path + "/cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")

    load_dotenv("token.env")
    bot.run(os.getenv('DISCORD_TOKEN'))