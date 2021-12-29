import validators

from discord.ext import commands
from discord import Embed
import discord

# types
from typing import Union
from discord.interactions import Interaction
from discord.message import Message
from discord.member import Member
from discord.channel import TextChannel

from db.user_management import get_user_by_project, add_project_to_user, remove_project_from_user

class ProjectDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def update_display_message(self, ctx) -> None:
        await ctx.send(content='\u200b', view=ProjectDisplayView())

class ProjectDisplayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Display a Project", style=discord.ButtonStyle.green, custom_id='project_display')
    async def display(self, button, interaction):
        await interaction.response.defer()

        user = interaction.user
        embed = await self.ask_to(user)
        if not embed:
            return

        project_msg = await interaction.channel.send(embed=embed, view=EditProject())
        add_project_to_user(user.id, project_msg.id)

        await interaction.delete_original_message()
        await interaction.channel.send(content="\u200b", view=self)

        await user.send("Project created succesfuly!")

    @staticmethod
    async def ask_to(user: Member) -> Union[Embed, None]:
        user = User(user)

        title = await user.ask(TitlePrompt)
        if not title:
            return

        description = await user.ask(DescriptionPrompt)
        if not description:
            return

        image = await user.ask(ImagePrompt)
        if not image:
            return

        link = await user.ask(LinkPrompt)
        if not link:
            return

        embed = ProjectDisplayView.create_embed(user.user, title, description, image, link)
        return embed

    @staticmethod
    def create_embed(user: Member, title: str, description: str, image: str, link: str) -> Embed:
        embed = Embed(title=title,
            description=description,
            url=link)

        embed.set_author(name=user.nick, icon_url=user.display_avatar.url)
        embed.set_footer(text="Do not forget to click on the project title to visit it!")
        embed.set_image(url=image)

        return embed

class User:
    def __init__(self, user):
        self.user = user

    async def ask(self, PromptType) -> str:
        prompt = PromptType()
        request_msg = await prompt.send_request_msg_to(self.user)
        
        await prompt.wait()
        if prompt.is_confirmed:
            response_msg = await prompt.get_response(request_msg.channel)
            await prompt.acknowledge(self.user, response_msg)

        else:
            await self.user.send("Goodbye!")
            return

        # TODO i dont like this because I createed acknowledge to avoid checking the type of prompt, but now I gotta check anyways
        if isinstance(prompt, ImagePrompt):
            return response_msg.attachments[-1].url

        return response_msg.content

class EditProject(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: Interaction) -> bool:
        owner = get_user_by_project(interaction.message.id)
        
        ID = 0
        if interaction.user.id != owner[ID] and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Only the owner can do this.", ephemeral=True)
            return False

        return True

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.grey, custom_id='edit_button')
    async def edit(self, button, interaction):
        await interaction.response.defer()
        
        embed = await ProjectDisplayView.ask_to(interaction.user)
        if not embed:
            return
        
        project_msg = interaction.message

        await project_msg.edit(embed=embed)
        await interaction.user.send("Project editted succesfuly!")

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger, custom_id=f'delete_button')
    async def delete(self, button, interaction):
        remove_project_from_user(interaction.user.id, interaction.message.id)
        await interaction.message.delete()

class Prompt(discord.ui.View):
    def __init__(self, prompt_type: str):
        super().__init__(timeout=None)
        self.is_confirmed = False
        self.error_msg = f"Send a {prompt_type} before confirming."
        self.prompt_type = prompt_type

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button, interaction):
        if not await self.is_valid(interaction):
            await self.send_error_msg(interaction)

        else:
            self.is_confirmed = True
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, button, interaction):
        self.stop()
    
    @staticmethod
    async def is_valid(interaction: Interaction) -> bool:
        msg = await Prompt.get_response(interaction.channel)
        return msg != interaction.message

    async def send_error_msg(self, interaction: Interaction) -> None:
        if self.error_msg not in interaction.message.content:
            await interaction.message.edit(content=interaction.message.content+f"\n*{self.error_msg}*")
        
    async def acknowledge(self, user: Member, response: Message) -> None:
        await user.send(f"You entered: {response.content}")

    @staticmethod
    async def get_response(channel: TextChannel) -> Message:
        msgs = await channel.history(limit=1).flatten()
        msg = msgs[0]

        return msg

    async def send_request_msg_to(self, user: Member) -> Message:
        return await user.send(f"Respond with the {self.prompt_type} of your project. If you make a mistake, edit or send a new message then confirm.",
            view=self)

class TitlePrompt(Prompt):
    def __init__(self):
        super().__init__("title")

class DescriptionPrompt(Prompt):
    def __init__(self):
        super().__init__("description")

class ImagePrompt(Prompt):
    def __init__(self):
        super().__init__("image")

        self.error_msg = "Attach and send an image before confirming."

    async def is_valid(self, interaction: Interaction) -> bool:
        msg = await self.get_response(interaction.channel)
        return msg != interaction.message and len(msg.attachments) != 0

    async def acknowledge(self, user, response: Message) -> None:
        image_url = response.attachments[-1].url
        await user.send(f"The image you attached is: \n> <{image_url}>")

class LinkPrompt(Prompt):
    def __init__(self):
        super().__init__("link")

        self.error_msg = 'Enter a valid "http" link before confirming.'

    async def is_valid(self, interaction: Interaction) -> bool:
        msg = await self.get_response(interaction.channel)
        return validators.url(msg.content) and msg != interaction.message

    async def acknowledge(self, user, response: Message) -> None:
        response = response.content
        await user.send(f"You entered: <{response}>")

def setup(bot):
    bot.add_cog(ProjectDisplay(bot))
    