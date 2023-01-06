import os 
import sys
from send_requests import send_request
from functions import copy_file
from postgres_updates import update_database

def send_to_endpoint(source, file, data, month, year, resource, database):
    '''
    Sends file to endpoint and updates Postgres database - only updates database if 200 is returned and file exists
    Endpoints: statements/ transactions/ holdings/ processed/
    Database Columns: statements holdings transactions processed
    '''

    pdf_file = lambda file : f"{file[:-5]}.pdf" if 'json' in file else (f"{file[:-4]}.pdf" if 'csv' in file else  file) 
      

    error_folder = { 
        'holdings' : '/home/ubuntu/Clients/.Autopopulate/holdings_errors',
        'transactions' : '/home/ubuntu/Clients/.Autopopulate/transactions_errors',
        'statements' : '/home/ubuntu/Clients/.Autopopulate/statements_errors',
    }    
          
    try:            
        if os.path.exists(os.path.join(f"{source}", file)):            
            if send_request(resource, os.path.join(source, file)) <= 299:
                update_database(data, pdf_file(file), database) 
            elif send_request(resource, os.path.join(source, file)) == 400:
                update_database(data, pdf_file(file), database)
            else:
                print(f"{send_request(resource, os.path.join(source, file))} -- {file}")                
                if not os.path.exists(os.path.join(error_folder[database], file)):                
                    copy_file(source, file, error_folder[database], file) 
        else:
            print(f"Missing File: {resource}")
    except Exception as error:     
             
        print(f"Endpoint Error: {resource} {file} {error.args}")

    
## sends JSON and CSV files from errors folders: Holdings and Transactions up to Autopopulate ##    
def errors_to_endpoint(source, file, data, resource, database):      
    pdf_file = lambda file : f"{file[:-5]}.pdf" if 'json' in file else (f"{file[:-4]}.pdf" if 'csv' in file else  file) 
                       
    if os.path.exists(os.path.join(f"{source}", file)):
        if send_request(resource, os.path.join(source, file)) <= 299:
            update_database(data, pdf_file(file), database) 
            os.remove(os.path.join(source, file))
        elif send_request(resource, os.path.join(source, file)) == 400:
            update_database(data, pdf_file(file), database) 
            os.remove(os.path.join(source, file))            
        else:
            print(f"{send_request(resource, os.path.join(source, file))} -- {file}")
            
    else:
        print(f"Missing File: {resource}")
    # except Exception as error:        cd 
    #     print(f"{resource} {file} {error.args}")