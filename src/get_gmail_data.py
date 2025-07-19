#############################################################################################################################################
# Command to run: pipenv run clingy --labels '{"category_promotions":"unread"}'                                                   #
#############################################################################################################################################

from __future__ import print_function
from time import perf_counter
from typing import Dict, Tuple

MAX_BATCHSIZE_TO_BE_DELETED = 20
MAX_BATCHSIZE_TO_BE_FETCHED = 50

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


def fetch_messages_per_label(label: Dict, service: object, labels_and_msg_types: Dict):
    """
    Takes a label dictionary and service object as arguments and fetches the messages per label.
    """
    delete_msgs_from_labels = list(labels_and_msg_types.keys())

    # t1_start = perf_counter()
    print("=====ENTERING V2=====")

    if label['name'].lower() in delete_msgs_from_labels:
        label_dtls = service.users().labels().get(userId="me", id=label['name']).execute()
        total_msg_count_in_label, unread_msg_count_in_label = label_dtls['messagesTotal'], label_dtls['messagesUnread']
        print("Total Messages in", label['name'], ":", total_msg_count_in_label)
        print("Unread Messages in", label['name'], ":", unread_msg_count_in_label)

        results = service.users().messages() \
                                        .list(userId = "me", \
                                            labelIds=label['name'], \
                                            # maxResults=MAX_BATCHSIZE_TO_BE_FETCHED, \
                                            q='is:{}'.format(labels_and_msg_types[label['name'].lower()])).execute()
                                            # q='is:{}'.format(labels_and_msg_types[label['name'].lower()])).execute()['messages']
        
    return results


def extract_message_metadata_from_labels(label: Dict, service: object, labels_and_msg_types: Dict) -> None:
    """
    Takes a label dictionary and service object as arguments and deletes the messages per label.
    """
    # delete_msgs_from_labels = list(labels_and_msg_types.keys())

    # # t1_start = perf_counter()
    # print("=====ENTERING V2=====")

    # if label['name'].lower() in delete_msgs_from_labels:
    #     label_dtls = service.users().labels().get(userId="me", id=label['name']).execute()
    #     total_msg_count_in_label, unread_msg_count_in_label = label_dtls['messagesTotal'], label_dtls['messagesUnread']
    #     print("Total Messages in", label['name'], ":", total_msg_count_in_label)
    #     print("Unread Messages in", label['name'], ":", unread_msg_count_in_label)

    #     results = service.users().messages() \
    #                                     .list(userId = "me", \
    #                                         labelIds=label['name'], \
    #                                         # maxResults=MAX_BATCHSIZE_TO_BE_FETCHED, \
    #                                         q='is:{}'.format(labels_and_msg_types[label['name'].lower()])).execute()
    #                                         # q='is:{}'.format(labels_and_msg_types[label['name'].lower()])).execute()['messages']

    results = fetch_messages_per_label(label, service, labels_and_msg_types)

    # print(results)
        
    # Fetch the first page of messages
    all_msgs_metadata_in_label = results['messages']
    for msg in all_msgs_metadata_in_label:
        yield msg

    while "nextPageToken" in results:
        page_token = results["nextPageToken"]

        results = (
            service.users().messages()
            .list(userId="me", q='is:{}'.format(labels_and_msg_types[label['name'].lower()]), pageToken=page_token)
            .execute()
        )
        if "messages" in results:
            for msg in results["messages"]:
                yield msg


def figure_out_name_of_func(label, service: object, labels_and_msg_types: Dict):
    """
    TODO: Weird func that needs to be named properly
    """
    extracted_msg_metadata_list = []
    print("Inside weirdly named function now")

    results = fetch_messages_per_label(label, service, labels_and_msg_types)

    # for msg in extract_message_metadata_from_labels(label, service, labels_and_msg_types):
    for msg in results['messages']:
        msg_to_be_deleted = service.users().messages().get(userId='me', id=msg['id']).execute()
        extracted_msg_metadata_dict = extract_message_contents(msg_to_be_deleted)
        extracted_msg_metadata_list.append(extracted_msg_metadata_dict)
        print("Length now: ", len(extracted_msg_metadata_list))

        if len(extracted_msg_metadata_list) == MAX_BATCHSIZE_TO_BE_FETCHED:
            break

    print("Exiting weirdly named function now")

    return extracted_msg_metadata_list


def do_actual_deletion(label, service: object, labels_and_msg_types: Dict):
    """
    Orchestrates the whole deletion process and calls `execute_batch_delete` to do the dirty work
    """
    msg_ids_in_label = {'ids':[]}
    ndeleted = 0
    for msg in extract_message_metadata_from_labels(label, service, labels_and_msg_types):
        msg_ids_in_label['ids'].append(msg['id'])

        if len(msg_ids_in_label['ids']) == MAX_BATCHSIZE_TO_BE_DELETED:
            execute_batch_delete(service, msg_ids_in_label)
            ndeleted += MAX_BATCHSIZE_TO_BE_DELETED
            msg_ids_in_label = {'ids':[]}
            print("batch deleted.")

    # Delete the last batch of messages.
    # if len(msg_ids_in_label['ids']) > 0:
    #     execute_batch_delete(service, msg_ids_in_label)
    #     ndeleted += len(msg_ids_in_label.keys())

    print(f"{ndeleted} messages deleted.")


def extract_message_metadata_from_labels_legacy(label: Dict, service: object, labels_and_msg_types: Dict) -> Tuple:
    """
    Takes a label dictionary and service object as arguments and deletes the messages per label.
    """
    delete_msgs_from_labels = list(labels_and_msg_types.keys())
    extracted_msg_metadata_list = []

    t1_start = perf_counter()

    if label['name'].lower() in delete_msgs_from_labels:
        label_dtls = service.users().labels().get(userId="me", id=label['name']).execute()
        total_msg_count_in_label, unread_msg_count_in_label = label_dtls['messagesTotal'], label_dtls['messagesUnread']
        print("Total Messages in", label['name'], ":", total_msg_count_in_label)
        print("Unread Messages in", label['name'], ":", unread_msg_count_in_label)

        all_msgs_metadata_in_label = service.users().messages() \
                                        .list(userId = "me", \
                                            labelIds=label['name'], \
                                            maxResults=MAX_BATCHSIZE_TO_BE_DELETED, \
                                            q='is:{}'.format(labels_and_msg_types[label['name'].lower()])).execute()['messages']
    
        msg_ids_in_label = {'ids':[]}

        for msg_metadata in all_msgs_metadata_in_label:
            msg_ids_in_label['ids'].append(msg_metadata['id'])
            msg_to_be_deleted = service.users().messages().get(userId='me', id=msg_metadata['id']).execute()
            extracted_msg_metadata_dict = extract_message_contents(msg_to_be_deleted)
            extracted_msg_metadata_list.append(extracted_msg_metadata_dict)

        t1_stop = perf_counter()
        print("Time taken: ", t1_stop - t1_start)

        return (msg_ids_in_label, extracted_msg_metadata_list)
                    