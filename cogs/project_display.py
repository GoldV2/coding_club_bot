from discord.ext import commands
from discord import Embed
import discord

class TitlePrompt(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]
        
        if msg == interaction.message:
            if not "Type a title before confirming" in interaction.message.content:
                await interaction.message.edit(content=interaction.message.content+"\n*Type a title before confirming.*")

        else:
            self.value = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.value = False
        self.stop()

class DescriptionPrompt(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]
        
        if msg == interaction.message:
            if not "Type a description before confirming" in interaction.message.content:
                await interaction.message.edit(content=interaction.message.content+"\n*Type a description before confirming.*")

        else:
            self.value = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.value = False
        self.stop()

class ImagePrompt(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]

        if msg == interaction.message or len(msg.attachments) == 0:
            if not "Attach an image or skip." in interaction.message.content:
                await interaction.message.edit(content=interaction.message.content+"\n*Attach an image or skip.*")
    
        else:
            self.value = True
            self.stop()

    @discord.ui.button(label='Skip', style=discord.ButtonStyle.grey)
    async def skip(self, button, interaction):
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.value = False
        self.stop()

class LinkPrompt(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        msgs = await interaction.channel.history(limit=1).flatten()
        msg = msgs[0]
        
        if msg == interaction.message:
            if not "Enter a link to your project." in interaction.message.content:
                await interaction.message.edit(content=interaction.message.content+"\n*Enter a link to your project.*")

        else:
            self.value = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.value = False
        self.stop()

class User:
    def __init__(self, user):
        self.user = user

    async def ask_title(self):
        prompt = TitlePrompt()
        msg = await self.user.send("Respond with the title of your project. If you make a mistake, feel free to edit the message or send another. Then confirm by pressing the appropriate button.",
            view=prompt)

        await prompt.wait()

        if prompt.value == False:
            await self.user.send("Goodbye!")
            return

        elif prompt.value == True:
            msgs = await msg.channel.history(limit=1).flatten()
            response = msgs[0]
            await self.user.send(f'The title of your project is "{response.content}"')

        return response.content

    async def ask_description(self):
        prompt = TitlePrompt()
        msg = await self.user.send("Respond with the description of your project. If you make a mistake, feel free to edit the message or send another. Then confirm by pressing the appropriate button.",
            view=prompt)

        await prompt.wait()

        if prompt.value == False:
            await self.user.send("Goodbye!")
            return

        elif prompt.value == True:
            msgs = await msg.channel.history(limit=1).flatten()
            response = msgs[0]
            await self.user.send(f'The description of your project is "{response.content}"')

        return response.content
        
    async def ask_image(self):
        prompt = ImagePrompt()
        msg = await self.user.send("Respond with an image of your project. If you make a mistake, feel free to edit the message or send another. Then confirm by pressing the appropriate button.",
            view=prompt)

        await prompt.wait()

        if prompt.value == False:
            await self.user.send("Goodbye!")
            return

        elif prompt.value == None:
            await self.user.send("No image attached.")
            return

        elif prompt.value == True:
            msgs = await msg.channel.history(limit=1).flatten()
            response = msgs[0]
            await self.user.send(f'The image of your project is "{response.attachments[-1].url}"')

        return response.attachments[-1].url

    async def ask_link(self):
        prompt = LinkPrompt()
        msg = await self.user.send("Respond with a link to your project. If you make a mistake, feel free to edit the message or send another. Then confirm by pressing the appropriate button.",
            view=prompt)

        await prompt.wait()

        if prompt.value == False:
            await self.user.send("Goodbye!")
            return

        elif prompt.value == True:
            msgs = await msg.channel.history(limit=1).flatten()
            response = msgs[0]
            await self.user.send(f'The link to your project is "{response.content}"')

        return response.content

class ProjectDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(self, user, title, description, image, link):
        embed = Embed(title=title,
            description=description,
            url=link)

        embed.set_author(name=user.nick, icon_url=user.display_avatar.url)
        embed.set_footer(text="Do not forget to click on the project title to visit it!")

        if image:
            embed.set_image(url=image)


        return embed

    @commands.command()
    async def display(self, ctx):
        user = User(ctx.author)
        title = await user.ask_title()
        description = await user.ask_description()
        image = await user.ask_image()
        link = await user.ask_link()

        embed = self.create_embed(user.user, title, description, image, link)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ProjectDisplay(bot))