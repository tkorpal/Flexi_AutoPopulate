from imports import *
import openpyxl
from openpyxl import load_workbook 

work = openpyxl.load_workbook("/home/ubuntu/FlexiAutoPopulate/Test Banks.xlsx")
 
wb = work.active

def json_uploads():
    try:
        for x in range(1,wb.max_row):
            year = '2021'
            month = '12'        
            file = wb[f"A{x}"].value        
            account = file.split(' ')[1].split('-')[0]
            json_file = f"{file.split('.')[0]}.json"   
            data = account_no_special(account, year)  
            if data:
                print(data) 
                source = f"{data[2]}{data[0]}/{year}/banking/{account}/.Autopopulate"             
                if os.path.exists(os.path.join(source, json_file)):
                    send_to_endpoint(source, json_file, data, month, year, 'holdings/', 'holdings')                
                    send_to_endpoint(source, json_file, data, month, year, 'transactions/', 'transactions')
                    update_to_null(file, 'processed')
    except:
        pass            

    
if __name__ == '__main__':
    json_uploads()