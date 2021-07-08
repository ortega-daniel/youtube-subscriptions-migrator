# Created by Daniel Ortega, July 2021
# ic.danielortega@gmail.com
 

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.readonly']
api_service_name = 'youtube'
api_version = 'v3'
client_secrets_file = 'client_secret.json'
max_results = 50

flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')

# get credentials for the old channel
credentials = flow.credentials

youtube = build(api_service_name, api_version, credentials=credentials)

# get list of subs from the old channel
old_subs = youtube.subscriptions().list(
    part='snippet',
    order='alphabetical',
    maxResults = max_results,
    mine=True
).execute()

# print ID from each channel in the result set
print(' Your subscriptions '.center(50, '='))
for sub in old_subs['items']:
    print(f'{sub["snippet"]["title"]} - {sub["snippet"]["resourceId"]["channelId"]}')


    

