from discord.ext import commands

class Forum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def something(self, ctx):
        components = {
    "content": "This is a message with components",
    "components": [
        {
            "type": 1,
            "components": [
                {
                    "type": 2,
                    "label": "Click me!",
                    "style": 1,
                    "custom_id": "click_one"
                }
            ]

        }
    ]
}

        await ctx.send(components=components)

def setup(bot):
    bot.add_cog(Forum(bot))