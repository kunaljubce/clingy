import os
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from get_gmail_data import delete_messages

# If modifying these scopes, delete the file token.json
SCOPES = ['https://mail.google.com/']

def main() -> None:
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    start_time = time.time()
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is created automatically when 
    # the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    delete_messages(labels, service)
    print("Time taken:", (time.time() - start_time), "seconds")

if __name__ == '__main__':
    main()