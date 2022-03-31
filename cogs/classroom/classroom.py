import os
from datetime import datetime

from discord.ext import commands, tasks
from discord import Embed, Color
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

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
        if not CREDENTIALS or not CREDENTIALS.valid:
            if CREDENTIALS and CREDENTIALS.expired and CREDENTIALS.refresh_token:
                CREDENTIALS.refresh(Request())
        
                with open(PATH + '/token.json', 'w') as token:
                    token.write(CREDENTIALS.to_json())
                    
        with build('classroom', 'v1', credentials=CREDENTIALS) as service:
            return f(*args, service, **kwargs)

    return wrapper

class Classroom(commands.Cog):
    
    ID = '396268373072'

    def __init__(self, bot):
        self.bot = bot
        self.teachers = self.get_teachers()

        self.send_post.start()

    # TODO refactor, there is prboably a better way to do this
    # TODO this way of doing this may cause problems in the future, so I need to grab all posts, sort by date, then post them on discord
    @with_service
    def get_all_posts(self, service):
        posts = []
        posts += service.courses().announcements().list(courseId=Classroom.ID).execute()['announcements']
        posts += service.courses().courseWork().list(courseId=Classroom.ID).execute()['courseWork']
        posts += service.courses().courseWorkMaterials().list(courseId=Classroom.ID).execute()['courseWorkMaterial']

        # 2021-10-26T01:31:43.872Z
        posts.sort(key=lambda post: datetime.strptime(post['creationTime'].split('T')[0], "%Y-%m-%d"))

        return posts

        # posted = Classroom.get_posted()
        # if announcement['id'] not in posted and announcement['state'] == 'PUBLISHED' and announcement['creatorUserId'] in self.teachers:
        #     return announcement

        # if (course_work['id'] not in posted and course_work['state'] == 'PUBLISHED'): # and course_work['creatorUserId'] in self.teachers):
        #     return course_work

        # # TODO checking for state may be redundant
        # if course_work_material['id'] not in posted and course_work['state'] == 'PUBLISHED' and course_work_material['creatorUserId'] in self.teachers:
        #     return course_work_material
    
        # # redundant
        # else:
        #     return None

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
    def get_topic_name(id: str, service) -> str:
        topics = service.courses().topics().list(courseId=Classroom.ID).execute()['topic']
        for topic in topics:
            if topic['topicId'] == id:
                return topic['name']

    # TODO create some type of global variable so I can make these methods static and not have to do bot.guilds[0]
    async def create_post_embed(self, post):
        # TODO delete this, for testing only
        if post['creatorUserId'] in self.teachers:
            creator = await self.bot.guilds[0].fetch_member(self.teachers[post['creatorUserId']])
        
        else:
            creator = await self.bot.guilds[0].fetch_member(250782339758555136)

        if 'title' in post:
            title = post['title']

        else:
            color = Color.red()
            title = 'Announcement'

        alternate_link = post['alternateLink']

        topic_name = ''
        if 'topicId' in post:
            topic_name = Classroom.get_topic_name(post['topicId'])

        # TODO find a way to combine this if-statement with the same one coming after
        if 'dueDate' in post:
            color = Color.green()
        
        if 'description' in post:
            color = Color.blue()

        embed = Embed(color=color, description=topic_name, title=title, url=alternate_link)

        embed.set_author(name=creator.nick, icon_url=creator.display_avatar.url)

        if 'text' in post:
            embed.add_field(name='Announcement', value=post['text'], inline=False)

        if 'description' in post:
            if '\n' in post['description']:
                embed.add_field(name='Description', value=post['description'][:post['description'].index('\n')] + ' (...)', inline=False)
            else:
                embed.add_field(name='Description', value=post['description'] + ' (...)', inline=False)

        if 'dueDate' in post:
            due_date = post['dueDate']
            day = f"{due_date['month']}/{due_date['day']}/{due_date['year']}"

            due_time = post['dueTime']
            time = f"{due_time['hours']}:{due_time['minutes'] if 'minutes' in due_time else '00'}"

            embed.add_field(name='Due Date', value=f'{day} by {time}')

        embed.set_footer(text='Not all information is displayed. Please click on the title for more information.')

        return embed

    @tasks.loop(minutes=30)
    async def send_post(self):
        posts = self.get_all_posts()
        posted = Classroom.get_posted()

        for post in posts:
            channel = await Helpers.get_channel(self.bot.guilds[0], '📢announcements📢')
            if post['id'] not in posted: 
                if 'title' in post:
                    if ('bi' in post['title'].lower()
                        and 'weekly' in post['title'].lower()
                        and '#' in post['title'].lower()):

                        channel = await Helpers.get_channel(self.bot.guilds[0], 'bi-weekly-challenges')
        

                embed = await self.create_post_embed(post)
                await channel.send(embed=embed)
                Classroom.add_post(post['id'])
            
    @send_post.before_loop
    async def before_tasks(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Classroom(bot))