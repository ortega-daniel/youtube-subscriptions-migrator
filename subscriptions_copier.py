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

# first run get next page token if it exists
try:
    next_page_token = old_subs['nextPageToken']
except KeyError:
    next_page_token = None

# list of dicts
subscriptions = []

# add each result to list
for sub in old_subs['items']:
    # subscriptions.append({channelTitle: channelId})
    subscriptions.append({sub['snippet']['title']: sub['snippet']['resourceId']['channelId']})

# get the next values on result set
while next_page_token:
    # request using nextPageToken
    old_subs = youtube.subscriptions().list(
        part='snippet',
        order='alphabetical',
        maxResults = max_results,
        pageToken = next_page_token,
        mine=True
    ).execute()

    # add each result to list
    for sub in old_subs['items']:
        # subscriptions.append({channelTitle: channelId})
        subscriptions.append({sub['snippet']['title']: sub['snippet']['resourceId']['channelId']})
        
    # if there are more pages get next page token
    try:
        next_page_token = old_subs['nextPageToken']
    except KeyError:
        next_page_token = None
    
print(subscriptions) 

