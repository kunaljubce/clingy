import sqlite3 as lite
from urllib.request import pathname2url

CREATE_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS message_details(
        msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def db_conn(label_name, query=None):
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
        cursor = sqliteConnection.cursor()
        print('Instance of SQLite DB initiated!')

        # Write a query and execute it with cursor
        query = 'Creating msg_details table...'
        sqliteConnection.execute(CREATE_TABLE_QUERY)

        # Fetch and output result
        result = cursor.fetchall()
        print(result)

        # Close the cursor
        cursor.close()

    # Handle errors
    except lite.Error as error:
        print('Error occurred - ', error)

    # Close DB Connection irrespective of success
    # or failure
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')

