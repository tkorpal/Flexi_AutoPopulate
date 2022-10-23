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

## Returns a list of banks that are set up for flexi
def flexi_uploads():    
    cursor.execute("""select Gpw_bankstrustsId from gpw_bankstrusts 
                        where gpw_FlexiCaptureUpload = ? """ , (1, ))
    return cursor.fetchall()

def account_no_special(account, year):
    '''
    data[0] = Client Number
    data[1] = BulkAbbr
    data[2] = Path
    data[3] = Bank Statement Number
    data[4] = Bank Name
    data[5] = Frequency: (1 = Monthly, 2 = Quarterly, 3 = Annually )
    data[6] = Bank Unique ID   
    data[7] = gpw_scheduledinexcel (True, False)
    
    '''
    cursor.execute('SELECT DISTINCT AccountNumber, Gpw_BulkAcctNameAbbrv, gpw_UbuntuPath, gpw_b_t_acctnum, \
                    gpw_banknameidName, gpw_frequencyreceived, gpw_banknameid, gpw_scheduledinexcel  \
                    FROM Account join Gpw_banking on Account.AccountId = Gpw_banking.gpw_clientnameid \
                    WHERE gpw_bankacct = ? and Gpw_stmtYrRecd = ? and gpw_banking.statuscode = ?' , (account, year, 1))
    data = cursor.fetchone()            
    return data

## uses bank statement account number to return client information
def get_bankstatement_info(statementnumber, year):
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
                    gpw_banknameidName, gpw_frequencyreceived, gpw_banknameid, gpw_scheduledinexcel  \
                    FROM Account join Gpw_banking on Account.AccountId = Gpw_banking.gpw_clientnameid \
                    WHERE gpw_b_t_acctnum = ? and Gpw_stmtYrRecd = ? and gpw_banking.statuscode = ?' , (statementnumber, year, 1))
    data = cursor.fetchone()            
    return data