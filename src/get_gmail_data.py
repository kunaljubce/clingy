#############################################################################################################################################
# Command to run: pipenv run python3 get_gmail_data.py --labels-and-types '{"category_promotions":"unread"}'                                #
#############################################################################################################################################

from __future__ import print_function
import json
import time
import os.path
import argparse
from typing import Dict
from archive_msg_metadata import db_conn

parser = argparse.ArgumentParser(description='Pass some parameters.')
parser.add_argument('--labels-and-types', default='{"spam":"all", "category_social":"all", "category_promotions":"all"}', type=json.loads, \
    help=r'Specify the label name(s) and their message type to be deleted in the format {"label_name":"message_type"}')
args = parser.parse_args()
labels_and_msg_types = args.labels_and_types
MAX_RESULTS_BATCHSIZE = 50

def extract_message_metadata(msg_object: object) -> Dict:
    """
    Extract important metadata from msg object to store in local DB for retrieval
    """
    headers_names_to_be_extracted = {
                        'From': 'from',
                        'Return-Path': 'return_path',
                        'Subject': 'subject',
                        'Date': 'date',
                        'To': 'to',
                        'Reply-To': 'reply_to',
                        'List-Unsubscribe': 'list_unsubscribe'
                    }
    msg_metadata = {}
    msg_metadata['msg_id'] = msg_object['id']
    msg_metadata['msg_snippet'] = msg_object['snippet']
    msg_headers = msg_object['payload']['headers']
    for header in msg_headers:
        if header['name'] in headers_names_to_be_extracted.keys():
            msg_metadata[headers_names_to_be_extracted[header['name']]] = header['value']

    return msg_metadata


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
                    msg_to_be_deleted = service.users().messages().get(userId='me', id=msg_metadata['id']).execute()
                    extracted_msg_metadata = extract_message_metadata(msg_to_be_deleted)
                    print(f"{extracted_msg_metadata}")
                    db_conn(label['id'])
                    #import sys
                    #sys.exit(1)
                    #service.users().messages().batchDelete(userId="me", body=msg_ids_in_label).execute()
                    