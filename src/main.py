import os
import json
import time
import argparse
from typing import Dict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.get_gmail_data import extract_message_metadata_from_labels, execute_batch_delete
from src.archive_msg_metadata import db_insert
from utils.welcome import welcome_screen
from src.export_archived_msgs_to_excel import export_archived_msgs

# If modifying these scopes, delete the file token.json
SCOPES = ['https://mail.google.com/']
YES_LIST = ['yes', 'y']
NO_LIST = ['no', 'n']

class Clingy:

    def __init__(self, credentials_file) -> None:
        self.creds = None
        self.credentials = credentials_file

    def authenticate(self):

        # The file token.json stores the user's access and refresh tokens, and is created automatically when 
        # the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def execute_clingy(self, label: Dict, service: object, labels_and_msg_types: Dict) -> None:
        '''
        Method to do the actual heavy lifting of Clingy. It gets called from main() and performs db archive of deleted 
        messages, takes in user input to provide summary of deleted messages in Excel, and invokes batch delete function. 
        '''
        export_messages_user_input = 'flag'

        # Out of all labels in inbox, only act on the labels mentioned by user
        if label['name'].lower() in list(labels_and_msg_types.keys()):
            msg_ids_in_label, extracted_msg_metadata_list = extract_message_metadata_from_labels(label, service, labels_and_msg_types)
            db_insert(label['name'], extracted_msg_metadata_list)

            print("Messages once deleted cannot be recovered!")
            print("Before deleting, would you prefer to take a look the message contents? (Y/Yes/N/No)")

            while export_messages_user_input not in (YES_LIST + NO_LIST):
                if not export_messages_user_input.__eq__('flag'):
                    print("Invalid input! Accepted responses are - Yes, Y, No, N - in any case!")
                export_messages_user_input = input("Provide your response...").lower()

            if export_messages_user_input in YES_LIST:
                export_archived_msgs(label['name'])

                # Get double confirmation from user before deleting
                confirm_deletion_user_input = input("Confirm deletion of messages? Enter Yes or Y to delete the messages shown in Excel, No or N to stop...").lower()
                while confirm_deletion_user_input not in (YES_LIST + NO_LIST):
                    confirm_deletion_user_input = input("Invalid input! Accepted responses are - Yes, Y, No, N - in any case! \n Confirm deletion? ").lower()
                if confirm_deletion_user_input in NO_LIST:
                    print("Clingy process terminating! Mails will not be deleted...")
                    return
            
            elif export_messages_user_input in NO_LIST:
                print("You have opted out of downloading the message contents before deletion!")

            print("Deleting messages...")

            execute_batch_delete(service, msg_ids_in_label)

    def main(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        start_time = time.time()

        parser = argparse.ArgumentParser(description='Pass some parameters.')
        parser.add_argument('--fetch-labels', default=False, type=bool, \
                    help=r'Mark as True if you want Clingy to fetch all label names in your inbox')
        parser.add_argument('--labels', default='{}', type=json.loads, \
                    help=r'Specify the label name(s) and their message type to be deleted in the format {"label_name":"message_type"}')
        args = parser.parse_args()
        labels_and_msg_types = args.labels
        fetch_all_labels = args.fetch_labels

        welcome_screen()
        self.authenticate()

        # Call the Gmail API
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            for label in labels:
                if fetch_all_labels:
                    print(label['name'])
                elif len(list(labels_and_msg_types.keys())) > 0:
                    self.execute_clingy(label, self.service, labels_and_msg_types)    
        
        print("Time taken:", (time.time() - start_time), "seconds")

if __name__ == '__main__':
    clingy = Clingy('credentials.json')
    clingy.main()