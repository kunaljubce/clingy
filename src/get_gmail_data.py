#############################################################################################################################################
# Command to run: pipenv run clingy --labels-and-types '{"category_promotions":"unread"}'                                                   #
#############################################################################################################################################

from __future__ import print_function
from typing import Dict, Tuple

MAX_RESULTS_BATCHSIZE = 50

def extract_message_contents(msg_object: object) -> Dict:
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


def execute_batch_delete(service: object, msg_ids_in_label: Dict) -> None:
    '''
    Executes batch delete functionality
    '''
    service.users().messages().batchDelete(userId="me", body=msg_ids_in_label).execute()


def extract_message_metadata_from_labels(label: Dict, service: object, labels_and_msg_types: Dict) -> Tuple:
    """
    Takes a label dictionary and service object as arguments and deletes the messages per label.
    """
    delete_msgs_from_labels = list(labels_and_msg_types.keys())
    extracted_msg_metadata_list = []

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
            extracted_msg_metadata_dict = extract_message_contents(msg_to_be_deleted)
            extracted_msg_metadata_list.append(extracted_msg_metadata_dict)

        return (msg_ids_in_label, extracted_msg_metadata_list)
                    