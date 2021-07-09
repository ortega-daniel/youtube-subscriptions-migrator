# Created by Daniel Ortega, July 2021
# ic.danielortega@gmail.com
 
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE_PATH = 'client_secret.json'
MAX_RESULTS = 50

# returns credentials from the OAuth2.0 session
def get_credentials(client_secrets_file, SCOPES, port=8080):
    # OAuth2.0 authentication flow
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    flow.run_local_server(port=port, prompt='consent', authorization_prompt_message='')

    return flow.credentials

# returns a list of dictionarys of the authenticated user's subsriptions
def get_subs_auth_account(credentials):
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # get list of subs from auth user
    subs = youtube.subscriptions().list(
        part='snippet',
        order='alphabetical',
        maxResults = MAX_RESULTS,
        mine=True
    ).execute()

    # if total results = 0 return None
    if not subs['pageInfo']['totalResults']:
        return None

    # first run get next page token if it exists
    try:
        next_page_token = subs['nextPageToken']
    except KeyError:
        # key error means subs <= MAX_RESULTS
        next_page_token = None
    
    subscriptions = []

    # add each result to list
    for sub in subs['items']:
        # [{channelTitle: channelId}]
        subscriptions.append({'title': sub['snippet']['title'], 'id': sub['snippet']['resourceId']['channelId']})

    # get the next values from result set
    while next_page_token:
        # request next {MAX_RESULTS} results using nextPageToken
        subs = youtube.subscriptions().list(
            part='snippet',
            order='alphabetical',
            maxResults = MAX_RESULTS,
            pageToken = next_page_token,
            mine=True
        ).execute()

        # add each result to list
        for sub in subs['items']:
            # [{channelTitle: channelId}]
            subscriptions.append({'title': sub['snippet']['title'], 'id': sub['snippet']['resourceId']['channelId']})
            
        try:
            # if there are more result pages get next page token
            next_page_token = subs['nextPageToken']
        except KeyError:
            # key error means no more result pages
            next_page_token = None

    return subscriptions

# get credentials for the old channel
credentials = get_credentials(CLIENT_SECRETS_FILE_PATH, SCOPES)
# get subscriptions list from the old channel
old_subs = get_subs_auth_account(credentials)

# if old subs list is empty
if not old_subs:
    print('You have no subscriptions to copy')
    sys.exit()

# get credentials for the new channel
credentials = get_credentials(CLIENT_SECRETS_FILE_PATH, SCOPES, port=8081)
# get subscriptions list from the new channel
new_subs = get_subs_auth_account(credentials)

new_subs_ids = []

# if new subs list is not empty
if new_subs:
    # create list containing the IDs of each channel the user is subscribe to
    for sub in new_subs:
        new_subs_ids.append(sub['id'])

# insert subs from old channel into new channel
youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
for sub in old_subs:
    if sub['id'] not in new_subs_ids:
        # insert subscription
        insert = youtube.subscriptions().insert(
            part="snippet",
            body={
                "snippet": {
                    "resourceId": {
                        "kind": "youtube#channel",
                        "channelId": sub['id']
                    }
                }
            }
        ).execute()

    print(f'New subscription added: {sub["title"]}')

print("that's all folks")


