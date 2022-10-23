from imports import *


def is_assetmark(data):
    if data[6] == 'E11899D9-EFEB-DD11-924D-00221912ADEF':
        return True
    return False

def upload_to_autopopulate(count=0):  
    source = '/home/ubuntu/flexicapture-downloads' 
    try:
        print('Send JSON to Autopopulate')
        for file in os.listdir(source):
            if (file.endswith('.json') or file.endswith('.JSON')): 
                account, year, month = file_info(file)        
                data = account_no_special(account, year)
                if check_data(source, file, data):
                    destination = check_folder(data, year, account)
                    if check_destination(source, file, destination):                
                        print(data) 
                        if is_assetmark(data):  
                            send_to_endpoint(source, file, data, month, year, 'holdings/', 'holdings')
                            move_file(source, file, destination, file ) 
                        else:                                                
                            send_to_endpoint(source, file, data, month, year, 'holdings/', 'holdings')                
                            send_to_endpoint(source, file, data, month, year, 'transactions/', 'transactions') 
                            move_file(source, file, destination, file )                        
        uploaded_to_autopop(f"Uploaded to Autopopulate",  count)  
    except Exception as error:       
        print(f"autopopulate  {error.args}")
     