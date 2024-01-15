import os
import sqlite3 as lite
from typing import List, Dict, Any
from urllib.request import pathname2url
from utils.config import get_clingy_app_download_path

db_folder_path = get_clingy_app_download_path()

CREATE_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS message_details(
        msg_id TEXT PRIMARY KEY,
        subject TEXT,
        sender_email TEXT,
        recipient_email TEXT,
        msg_snippet BLOB,
        msg_receipt_date TEXT,
        reply_to TEXT,
        list_unsubscribe TEXT,
        return_path TEXT,
        record_insert_date DATETIME,
        archival_cycle TEXT
    );
'''

INSERT_MSG_METADATA_QUERY = '''
    INSERT INTO message_details 
    VALUES ('{msg_id}',
            '{subject}',
            '{sender_email}',
            '{recipient_email}',
            '{msg_snippet}',
            '{msg_receipt_date}',
            '{reply_to}',
            '{list_unsubscribe}',
            '{return_path}',
            STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
            'C');
'''

# archival_cycle = 'P' for all previous archived messages. Before inserting new records, we update
#    all existing records to 'P'
# archival_cycle = 'C' for current batch of messages to be archived
UPDATE_TABLE_QUERY = '''
    UPDATE message_details
    SET archival_cycle = 'P'
    WHERE archival_cycle = 'C';
'''

def db_conn(label_name: str) -> object:
    """
    Setup SQLite DB connection and create message_details table if not exists.
    Inputs: label_name -> This attribute is used to create seperate DBs for each label.
            TODO: Explore the possibility of one DB and multiple schemas/tables.
    """
    db_name = f'gmail_{label_name.lower()}.db'
    db_path = os.path.join(db_folder_path, db_name)

    # Connect to DB and create a connection object
    sqliteConnection = lite.connect(db_path)
    print('Instance of SQLite DB initiated!')
            
    return sqliteConnection

def db_insert(label_name: str, msg_metadata_list: List[Dict[str, Any]]) -> None:

    list_of_insert_queries = []
    for msg_metadata in msg_metadata_list:
        insert_query = INSERT_MSG_METADATA_QUERY.format(
                                msg_id = msg_metadata.get('msg_id'),
                                subject = msg_metadata.get('subject', '').replace("'", '"'),
                                sender_email = msg_metadata.get('from').replace("'", '"'),
                                recipient_email = msg_metadata.get('to', '').replace("'", '"'),
                                msg_snippet = msg_metadata.get('msg_snippet', '').replace("'", '"'),
                                msg_receipt_date = msg_metadata.get('date'),
                                reply_to = msg_metadata.get('reply_to', '').replace("'", '"'),
                                list_unsubscribe = msg_metadata.get('list_unsubscribe', '').replace("'", '"'),
                                return_path = msg_metadata.get('return_path', '').replace("'", '"')
                            )
        list_of_insert_queries.append(insert_query)

    str_of_insert_queries = ''.join(list_of_insert_queries)

    query = 'Creating msg_details table...'

    with db_conn(label_name) as sqliteConnObj:
        sqliteConnObj.execute(CREATE_TABLE_QUERY)
        cursor = sqliteConnObj.cursor()
        cursor.execute(UPDATE_TABLE_QUERY)
        cursor.executescript(str_of_insert_queries)
