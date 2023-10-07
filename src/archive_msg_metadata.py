import sqlite3 as lite
from typing import List
from urllib.request import pathname2url

CREATE_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS message_details(
        msg_id TEXT PRIMARY KEY, --AUTOINCREMENT
        subject TEXT,
        sender_email TEXT,
        recipient_email TEXT,
        msg_snippet BLOB,
        date TEXT,
        reply_to TEXT,
        list_unsubscribe TEXT,
        return_path TEXT
    );
'''


INSERT_MSG_METADATA_QUERY = '''
    INSERT INTO message_details 
    VALUES ('{msg_id}',
            '{subject}',
            '{sender_email}',
            '{recipient_email}',
            '{msg_snippet}',
            '{date}',
            '{reply_to}',
            '{list_unsubscribe}',
            '{return_path}')
'''

def db_conn(label_name, msg_metadata):
    """
    Setup SQLite DB connection and create message_details table if not exists.
    Inputs: label_name -> This attribute is used to create seperate DBs for each label.
            TODO: Explore the possibility of one DB and multiple schemas/tables.
    """
    db_name = f'gmail_{label_name.lower()}.db' 
    """ try:
        db_uri = 'file:{}?mode=rw'.format(pathname2url(db_name))
        # Connect to DB and create a cursor
        sqliteConnection = lite.connect(db_uri, uri=True)
        print("DB exists!")
    
    except lite.OperationalError:
        db_uri = 'file:{}?mode=rwc'.format(pathname2url(db_name))
        # Connect to DB and create a cursor
        sqliteConnection = lite.connect(db_uri, uri=True)
        print("Creating DB!")"""

    try:
        # Connect to DB and create a cursor
        sqliteConnection = lite.connect(db_name)
        print('Instance of SQLite DB initiated!')

        query = 'Creating msg_details table...'
        cursor = sqliteConnection.cursor()
        sqliteConnection.execute(CREATE_TABLE_QUERY)
        result = cursor.fetchall()
        
        insert_query = INSERT_MSG_METADATA_QUERY.format(
                                msg_id = msg_metadata.get('msg_id'),
                                subject = msg_metadata.get('subject', '').replace("'", '"'),
                                sender_email = msg_metadata.get('from').replace("'", '"'),
                                recipient_email = msg_metadata.get('to', '').replace("'", '"'),
                                msg_snippet = msg_metadata.get('msg_snippet', '').replace("'", '"'),
                                date = msg_metadata.get('date'),
                                reply_to = msg_metadata.get('reply_to', '').replace("'", '"'),
                                list_unsubscribe = msg_metadata.get('list_unsubscribe', '').replace("'", '"'),
                                return_path = msg_metadata.get('return_path', '').replace("'", '"')
                            )
        
        cursor.execute(insert_query)
        #print(insert_query)
        print("Message ID - {msg_id} - inserted into table!".format(msg_id=msg_metadata.get('msg_id')))
        cursor.close()

    # Handle errors
    except lite.Error as error:
        print('Error occurred - ', error)

    # Close DB Connection irrespective of success or failure
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')

""" def db_insert(sqliteConnObj: object):
    with sqliteConnObj.cursor() as cursor:

 """