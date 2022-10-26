from imports import *
import pandas as pd
import psycopg2
from datetime import date
 

today = date.today()

conn = psycopg2.connect(
    host = os.environ.get('azure_host'),
    database = os.environ.get('azure_database_auto'),
    user = os.environ.get('azure_user_auto'),
    password = os.environ.get('azure_password_auto')
    )           
cursor = conn.cursor()

## returns of list for statement for bank, month, year and processed not NULL
def list_files(bank_id, month, year):
    try:
        list_files_query = """ select * from file_status where bank_id = %s and month = %s and 
                year = %s and processed is not NULL """
        cursor.execute(list_files_query, ( bank_id, month, year))
        data = cursor.fetchall()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error) 

## If xlsx is empty dataframe will upload json to holdings and transactions ##
def check_empty(bank_id, month, year, not_empty=0, empty=0):
    get_files = list_files(bank_id, month, year)
    try:
        for x in get_files:         
            account = x[2].split('-')[0].split(' ')[1]
            xlsx_file = f"{x[2][:-4]}_AUTOPOPULATE.xlsx" 
            file = f"{x[2][:-4]}.json"  
            pdf =  x[2][:-4]  + '.pdf'     
            data = account_no_special(account, year)
            if data: 
                source = f"{data[2]}{data[0]}/{year}/Banking/{account}/.Autopopulate" 
                # print(os.path.join(source, xlsx_file))          
                if os.path.exists(os.path.join(source, xlsx_file )):
                    df = pd.read_excel(os.path.join(source, xlsx_file ))
                    result = df.empty
                    if result:
                        empty +=1
                        # if os.path.exists(os.path.join(source,file )):
                        #     empty +=1
                            # print(data)                         
                            # send_to_endpoint(source, file, data, month, year, 'holdings/', 'holdings')                
                            # send_to_endpoint(source, file, data, month, year, 'transactions/', 'transactions')
                            # update_to_null(str(pdf), 'processed')
                            # print(f"{xlsx_file} - {result}") 
                                        
                    else:
                        not_empty  +=1
                        # print(f"{xlsx_file} - {result}")        
    except IOError as error:       
        print(f"Empty Excel  {error.args}")
        
    print(f"Empty: {empty}") 
    print(f"Not Empty: {not_empty}")
 
bank_id = '0E8F3927-258D-E311-ACA0-782BCB14085F'
month = '01'
year = '2022'        
        
if __name__ == '__main__':
    check_empty(bank_id, month, year)
    
    
