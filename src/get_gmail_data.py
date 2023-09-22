#############################################################################################################################################
# Command to run: pipenv run python3 get_gmail_data.py --labels-and-types '{"category_promotions":"unread"}'                                #
#############################################################################################################################################

from __future__ import print_function
import json
import time
import os.path
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

parser = argparse.ArgumentParser(description='Pass some parameters.')
parser.add_argument('--labels-and-types', default='{"spam":"all", "category_social":"all", "category_promotions":"all"}', type=json.loads, \
    help=r'Specify the label name(s) and their message type to be deleted in the format {"label_name":"message_type"}')
args = parser.parse_args()
labels_and_msg_types = args.labels_and_types
MAX_RESULTS_BATCHSIZE = 50

# If modifying these scopes, delete the file token.json
SCOPES = ['https://mail.google.com/']

def delete_messages(labels: object, service: object) -> None:
    """
    Takes the label names and service object as arguments and deletes the messages per label.
    """
    delete_msgs_from_labels = list(labels_and_msg_types.keys())

    if not labels:
        print('No labels found.')
    else:
        for label in labels:
            if label['name'].lower() in delete_msgs_from_labels:
                label_dtls = service.users().labels().get(userId="me", id=label['name']).execute()
                total_msg_count_in_label, unread_msg_count_in_label = label_dtls['messagesTotal'], label_dtls['messagesUnread']
                print("Total Messages in", label['name'], ":", total_msg_count_in_label)
                print("Unread Messages in", label['name'], ":", unread_msg_count_in_label)

                all_msgs_metadata_in_label = service.users().messages() \
                                                .list(userId = "me", \
                                                    labelIds=label['name'], \
                                                    maxResults=MAX_RESULTS_BATCHSIZE, \
                                                    q='is:{}'.format(labels_and_msg_types[label['name'].lower()])).execute()['messages']
            
                msg_ids_in_label = {'ids':[]}
                for msg_metadata in all_msgs_metadata_in_label:
                    msg_ids_in_label['ids'].append(msg_metadata['id'])
                    service.users().messages().batchDelete(userId="me", body=msg_ids_in_label).execute()


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