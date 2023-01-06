import os
import re
import shutil
import sys
import pyodbc
import datetime
import xlwt
from xlwt import Workbook
from PyPDF2 import PdfFileReader, PdfFileWriter
from queries import get_bankstatement_info, account_no_special, to_upload
from functions import pdf_writer, move_file, check_data, check_folder, check_destination, file_info
from postgres_updates import flexicapture_database, record_exists, scheduled_statements, update_to_null, update_database, delete_filename
from endpoints import send_to_endpoint, errors_to_endpoint
from emails import uploaded_to_flexi, uploaded_to_autopop
from send_requests import schedule_d
from assetmark import main 
from postgres_auto import delete_autopopulate_record
 

# user = os.environ.get('sql_user')
# password = os.environ.get('sql_password')

# conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=10.10.10.24;Database=GPWA_MSCRM;UID=%s;PWD=%s" % (user, password))
# cursor = conn.cursor()