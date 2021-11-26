from discord.ext import commands
from discord import Embed
import discord

# types
from types import NoneType

from discord.interactions import Interaction
from discord.message import Message
from discord.member import Member
from discord.channel import TextChannel

from db.user_management import get_user_by_project, add_project_to_user, remove_project_from_user

class Prompt(discord.ui.View):
    def __init__(self, prompt_type: str):
        super().__init__(timeout=None)
        self.is_confirmed = None
        self.prompt_type = prompt_type
        self.error_msg = self.create_error_msg()

    async def send_request_msg_to(self, user: Member) -> Message:
        return await user.send(f"Respond with the {self.prompt_type} of your project. If you make a mistake, edit or write a new message then confirm.",
            view=self)

    def create_error_msg(self) -> str:
        return f"Enter a {self.prompt_type} before confirming."

    @staticmethod
    async def get_response(channel: TextChannel) -> Message:
        msgs = await channel.history(limit=1).flatten()
        msg = msgs[0]

        return msg

    @staticmethod
    async def is_valid(interaction: Interaction) -> bool:
        msg = await Prompt.get_response(interaction.channel)
        return msg != interaction.message

    async def send_error_msg(self, interaction: Interaction) -> NoneType:
        if self.error_msg not in interaction.message.content:
            await interaction.message.edit(content=interaction.message.content+f"\n*{self.error_msg}*")
        
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        if not await self.is_valid(interaction):
            await self.send_error_msg(interaction)

        else:
            self.is_confirmed = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.is_confirmed = False
        self.stop()

class TitlePrompt(Prompt):
    def __init__(self):
        super().__init__("title")

class DescriptionPrompt(Prompt):
    def __init__(self):
        super().__init__("description")

class ImagePrompt(Prompt):
    def __init__(self):
        super().__init__("image")

    @staticmethod
    def create_error_msg() -> str:
        return "Attach an image before confirming."

    async def is_valid(self, interaction: Interaction) -> bool:
        msg = await self.get_response(interaction.channel)
        return msg != interaction.message and len(msg.attachments) != 0

class LinkPrompt(Prompt):
    def __init__(self):
        super().__init__("link")

    @staticmethod
    def create_error_msg():
        return 'Enter a valid "http" link before confirming.'

    async def is_valid(self, interaction: Interaction) -> bool:
        msg = await self.get_response(interaction.channel)
        return ("http" in msg.content and msg != interaction.message)

class EditProject(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: Interaction) -> bool:
        owner = get_user_by_project(interaction.message.id)
        
        ID = 0
        if interaction.user.id != owner[ID]:
            await interaction.response.send_message("Only the owner can do this.", ephemeral=True)
            return False

        return True

    # TODO raises discord.errors.NotFound: 404 Not Found (error code: 10062): Unknown interaction
    # works just fine though
    @discord.ui.button(label='Edit', style=discord.ButtonStyle.grey, custom_id=f'edit_button')
    async def edit(self, button, interaction):
        embed = await ProjectDisplay.ask_to(interaction.user)
        if not embed:
            return
        
        project_msg = interaction.message

        await project_msg.edit(embed=embed)
        await interaction.user.send("Project editted succesfuly!")

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger, custom_id=f'delete_button')
    async def delete(self, button, interaction):
        remove_project_from_user(interaction.user.id, interaction.message.id)
        await interaction.message.delete()

class User:
    def __init__(self, user):
        self.user = user

    async def ask(self, PromptType: Prompt) -> str:
        prompt = PromptType()
        request_msg = await prompt.send_request_msg_to(self.user)
        
        await prompt.wait()
        if prompt.is_confirmed:
            response_msg = await prompt.get_response(request_msg.channel)

            # if this function is asking for an image
            if PromptType == ImagePrompt:
                image_url = response_msg.attachments[-1].url
                await self.user.send(f"The image you attached is: {image_url}")
                return image_url

            else:
                await self.user.send(f"You entered: {response_msg.content}")

        else:
            await self.user.send("Goodbye!")
            return ''

        return response_msg.content

class ProjectDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def create_embed(user: Member, title: str, description: str, image: str, link: str) -> Embed:
        embed = Embed(title=title,
            description=description,
            url=link)

        embed.set_author(name=user.nick, icon_url=user.display_avatar.url)
        embed.set_footer(text="Do not forget to click on the project title to visit it!")
        embed.set_image(url=image)

        return embed

    @staticmethod
    async def ask_to(user: Member) -> Embed: # TODO returns Embed or bool
        user = User(user)

        title = await user.ask(TitlePrompt)
        if not title:
            return False

        description = await user.ask(DescriptionPrompt)
        if not description:
            return False

        image = await user.ask(ImagePrompt)
        if not image:
            return False

        link = await user.ask(LinkPrompt)
        if not link:
            return False

        embed = ProjectDisplay.create_embed(user.user, title, description, image, link)
        return embed

    @commands.command()
    async def display(self, ctx) -> NoneType:
        user = ctx.author
        embed = await ProjectDisplay.ask_to(user)
        if not embed:
            return

        project_msg = await ctx.send(embed=embed, view=EditProject())

        add_project_to_user(user.id, project_msg.id)

        await user.send("Project created succesfuly!")
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(ProjectDisplay(bot))
    