import sqlite3

CREATE_TABLE_QUERY = '''
    CREATE TABLE message_details(
        from TEXT,
        return_path TEXT,
        subject TEXT,
        date DATE,
        to TEXT,
        reply_to TEXT,
        list_unsubscribe TEXT
    )
'''

def db_conn(label_name, query=None):
    db_name = f'gmail_+{label_name}.db' 
    try:

        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect(db_name)
        cursor = sqliteConnection.cursor()
        print('Instance of SQLite DB initiated!')

        # Write a query and execute it with cursor
        query = 'select sqlite_version();'
        cursor.execute(query)

        # Fetch and output result
        result = cursor.fetchall()
        print('SQLite Version is {}'.format(result))

        # Close the cursor
        cursor.close()

    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)

    # Close DB Connection irrespective of success
    # or failure
    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')
