import pandas as pd
from typing import List
from sqlalchemy import MetaData, create_engine, Table, sql, select
from archive_msg_metadata import db_insert, db_conn

# TODO: To be replaced with an option for user to export these results to an Excel and download on local
SHOW_10_ROWS_QUERY = '''SELECT * FROM message_details LIMIT 10'''

def print_archived_msgs_on_console(label_name: str):

    with db_conn(label_name) as sqliteConnObj:
        cursor = sqliteConnObj.cursor()
        cursor.execute(SHOW_10_ROWS_QUERY)

        print('All Rows Inserted: \n')

        output = cursor.fetchall()
        for row in output:
            print(row)

def export_archived_msgs(label_name: List):

    db_name = f'gmail_{label_name.lower()}.db' 
    excel_file = f'gmail_{label_name.lower()}.xlsx' 
    engine = create_engine(f'sqlite:///{db_name}')

    print(f"Downloading {excel_file}...")
    df = pd.read_sql_table('message_details', engine)

    # Drop msg_id from being on excel as it makes no sense to the user
    df.drop('msg_id', axis=1, inplace=True)
    
    df.to_excel(excel_file, index=False)
