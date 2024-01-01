import os
import time
from typing import Dict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from get_gmail_data import extract_message_metadata_from_labels, execute_batch_delete, labels_and_msg_types
from archive_msg_metadata import db_insert
from export_archived_msgs_to_excel import export_archived_msgs

# If modifying these scopes, delete the file token.json
SCOPES = ['https://mail.google.com/']

def execute_clingy(label: Dict, service: object) -> None:
    '''
    Function to do the actual heavy lifting of Clingy. It gets called from main() and performs db archive of deleted 
    messages, takes in user input to provide summary of deleted messages in Excel, and invokes batch delete function. 
    '''
    export_messages_user_input = 'flag'

    # Out of all labels in inbox, only act on the labels mentioned by user
    if label['name'].lower() in list(labels_and_msg_types.keys()):
        msg_ids_in_label, extracted_msg_metadata_list = extract_message_metadata_from_labels(label, service)
        db_insert(label['id'], extracted_msg_metadata_list)

        print("Messages once deleted cannot be recovered!")
        print("Before deleting, would you prefer to take a look the message contents? (Y/Yes/N/No)")

        while export_messages_user_input not in ['yes', 'y', 'no', 'n']:
            if not export_messages_user_input.__eq__('flag'):
                print("Invalid input! Accepted responses are - Yes, Y, No, N - in any case!")
            export_messages_user_input = input("Provide your response...").lower()

        if export_messages_user_input in ['yes', 'y']:
            export_archived_msgs(label['id'])
        elif export_messages_user_input in ['no', 'n']:
            print("You have opted out of downloading the message contents before deletion!")

        print("Deleting messages...")

        execute_batch_delete(service, msg_ids_in_label)


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

    if not labels:
        print('No labels found.')
    else:
        for label in labels:
            execute_clingy(label, service)    
    
    print("Time taken:", (time.time() - start_time), "seconds")

if __name__ == '__main__':
    main()