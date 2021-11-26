from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

flow = InstalledAppFlow.from_client_secrets_file(
    '/home/thinkland/bots/coding_club_bot/cogs/classroom/credentials.json',
    scopes = ['https://www.googleapis.com/auth/classroom.courses.readonly',
              'https://www.googleapis.com/auth/classroom.course-work.readonly',
              'https://www.googleapis.com/auth/classroom.announcements.readonly',
              'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
              'https://www.googleapis.com/auth/classroom.topics.readonly'])

flow.run_local_server()
credentials = flow.credentials

with build('calendar', 'v3', credentials=credentials) as service:
    print(service)