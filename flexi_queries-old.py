import pyodbc
import datetime
import os

user = os.environ.get('sql_user')
password = os.environ.get('sql_password')

conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=10.10.10.24;Database=GPWA_MSCRM;UID=%s;PWD=%s" % (user, password))
cursor = conn.cursor()

## FlexiCapture ##
## used to determine if file needs to be uploaded to flexicaputure
def to_upload(data):    
    cursor.execute('select gpw_FlexiCaptureUpload from Gpw_bankstrusts \
                    WHERE Gpw_bankstrustsId = ? ' , (data[6], ))
    results = cursor.fetchone()  
    if results[0] and data[7]:
        return True                  
    return False

def account_no_special(account, year):
    '''
    data[0] = Client Number
    data[1] = BulkAbbr
    data[2] = Path
    data[3] = Bank Statement Number
    data[4] = Bank Name
    data[5] = Frequency: (1 = Monthly, 2 = Quarterly, 3 = Annually )
    data[6] = Statement Unique ID 
    data[7] = gpw_scheduledinexcel
    '''

    cursor.execute('SELECT DISTINCT AccountNumber, Gpw_BulkAcctNameAbbrv, gpw_UbuntuPath, gpw_b_t_acctnum, \
                    gpw_banknameidName, Account.StatusCode, gpw_excelcsvavailable, gpw_scheduledinexcel, gpw_frequencyreceived, \
                    gpw_scheduledinexcel FROM Account join Gpw_banking on Account.AccountId = Gpw_banking.gpw_clientnameid \
                    WHERE gpw_bankacct = ? and Gpw_stmtYrRecd = ? and gpw_banking.statuscode = ?' , (account, year, 1))
    data = cursor.fetchone()            
    return data