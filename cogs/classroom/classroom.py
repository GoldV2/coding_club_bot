import os

from discord.ext import commands, tasks
from discord.embeds import Embed
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from cogs.helpers import Helpers

# types
from typing import Dict, List

PATH = os.path.dirname(os.path.realpath(__file__))
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.course-work.readonly',
          'https://www.googleapis.com/auth/classroom.announcements.readonly',
          'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
          'https://www.googleapis.com/auth/classroom.topics.readonly',
          'https://www.googleapis.com/auth/classroom.rosters.readonly']
CREDENTIALS = Credentials.from_authorized_user_file(PATH + '/token.json', SCOPES)

def with_service(f):
    def wrapper(*args, **kwargs):
        with build('classroom', 'v1', credentials=CREDENTIALS) as service:
            return f(service, *args, **kwargs)

    return wrapper

class Classroom(commands.Cog):
    
    ID = '396268373072'

    def __init__(self, bot):
        self.bot = bot
        self.teachers = self.get_teachers()

        self.send_post.start()

    # TODO refactor, there is prboably a better way to do this
    @with_service
    @staticmethod
    def get_last_post(service):
        announcement = service.courses().announcements().list(courseId=Classroom.ID, pageSize=1).execute()['announcements'][0]
        # pageSize = 1
        course_work = service.courses().courseWork().list(courseId=Classroom.ID, pageSize=10).execute()['courseWork'] # [0]
        course_work_material = service.courses().courseWorkMaterials().list(courseId=Classroom.ID, pageSize=1).execute()['courseWorkMaterial'][0]

        for cw in course_work:
            if cw['creatorUserId'] == '110004525941236336917':
                course_work = cw
                break

        posted = Classroom.get_posted()
        # if announcement['id'] not in posted and announcement['state'] == 'PUBLISHED':
        #     return announcement

        if course_work['id'] not in posted and course_work['state'] == 'PUBLISHED':
            return course_work

        # TODO checking for state may be redundant
        if course_work_material['id'] not in posted and course_work['state'] == 'PUBLISHED':
            return course_work_material
    
        # redundant
        else:
            return None

    @staticmethod
    def get_teachers() -> Dict[str, int]:
        GOOGLE_ID = 0
        DISCORD_ID = 1
        with open(PATH + '/teachers.txt', 'r') as f:
            return {teacher[GOOGLE_ID]: int(teacher[DISCORD_ID]) for teacher in [line.strip().split() for line in f.readlines()]}

    @staticmethod
    def get_posted() -> List[str]:
        with open(PATH + '/posted.txt', 'r') as f:
            return [line.strip() for line in f.readlines()]

    @staticmethod
    def add_post(id: str) -> None:
        with open(PATH + '/posted.txt', 'a+') as f:
            # checking something was already posted
            f.seek(0)
            posted = f.read(1)
            if len(posted) > 0:
                f.write("\n")

            f.write(id)

    # TODO add raise exceptions, in this case, raise an exception if not topic with such id
    @with_service
    @staticmethod
    def get_topic_name(service, id: str) -> str:
        topics = service.courses().topics().list(courseId=Classroom.ID).execute()['topic']
        for topic in topics:
            if topic['topicId'] == id:
                return topic['name']

    # TODO create some type of global variable so I can make these methods static and not have to do bot.guilds[0]
    async def create_post_embed(self, post):
        creator = await self.bot.guilds[0].fetch_member(self.teachers[post['creatorUserId']])
        
        if 'title' in post:
            title = post['title']

        else:
            title = 'Announcement'

        alternate_link = post['alternateLink']

        topic_name = Classroom.get_topic_name(post['topicId'])

        # TODO make them color coded by topic
        embed = Embed(description=topic_name, title=title, url=alternate_link)

        embed.set_author(name=creator.nick, icon_url=creator.display_avatar.url)

        if 'text' in post:
            embed.add_field(name='Announcement', value=post['text'], inline=False)

        if 'description' in post:
            embed.add_field(name='Description', value=post['description'][:post['description'].index('\n')], inline=False)

        if 'dueDate' in post:
            due_date = post['dueDate']
            day = f"{due_date['month']}/{due_date['day']}/{due_date['year']}"

            due_time = post['dueTime']
            time = f"{due_time['hours']}:{due_time['minutes']}"

            embed.add_field(name='Due Date', value=f'{day} by {time}')

        embed.set_footer(text='Click on the post title for more information.')

        return embed

    @tasks.loop(seconds=30)
    async def send_post(self):
        post = Classroom.get_last_post()
        
        if post:
            channel = await Helpers.get_channel(self.bot.guilds[0], '📢announcements📢')
            embed = await self.create_post_embed(post)
            await channel.send(embed=embed)
            Classroom.add_post(post['id'])
            
    @commands.command()
    async def print_commands(self, ctx):
        for command in self.bot.walk_commands():
            print(command)

    @send_post.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Classroom(bot))