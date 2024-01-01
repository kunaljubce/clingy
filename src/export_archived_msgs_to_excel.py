import os
import pandas as pd
from typing import List
from datetime import datetime as dt
from sqlalchemy import MetaData, create_engine, Table, sql, select
from archive_msg_metadata import db_conn
from utils.config import get_clingy_app_download_path

# TODO: To be replaced with an option for user to export these results to an Excel and download on local
QUERY_GET_ALL_ARCHIVED_MSG_DETAILS = '''SELECT * FROM message_details'''
QUERY_GET_CURRENT_ARCHIVAL_MSG_BATCH = "SELECT * FROM message_details WHERE archival_cycle = 'C'"
download_path = get_clingy_app_download_path()

def export_archived_msgs(label_name: str, all_msgs: bool = False) -> None:

    label_name = label_name.lower()
    current_datetime = dt.now().strftime('%Y%m%d_%H%M%S')
    db_name = f'gmail_{label_name}.db' 
    excel_file = os.path.join(download_path, f'gmail_{label_name}_{current_datetime}.xlsx')
    engine = create_engine(f'sqlite:///{db_name}')

    print(f"Saving details of messages to be deleted in {excel_file}...")
    if all_msgs:
        df = pd.read_sql_query(QUERY_GET_ALL_ARCHIVED_MSG_DETAILS, engine)
    else:
        df = pd.read_sql_query(QUERY_GET_CURRENT_ARCHIVAL_MSG_BATCH, engine)

    # Drop msg_id from being on excel as it makes no sense to the user
    df.drop('msg_id', axis=1, inplace=True)

    df.to_excel(excel_file, index=False)
