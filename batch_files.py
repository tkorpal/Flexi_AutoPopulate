import os
import shutil
import sys

import xlwt
from xlwt import Workbook
  
# Workbook is created
wb = Workbook()
  
# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Sheet 1')

sys.path.append('/home/ubuntu/ProcessingSite/Shared_Processes/queries') 
from bankingSQL import account_no_special  

sys.path.append('/home/ubuntu/ProcessingSite/Schedule_D')
from postgres_updates import json_processed, missing_in_database

def file_info(filename):
    return filename.split('-')[0].split(' ')[1], filename[:4], filename[4:6] 

## 
def batch_files_json_exists(count=0):
    source = upload = f"/home/ubuntu/batch-files"    
    for root, subdirectories, files in os.walk(source):
        for subdirectory in subdirectories:
            folders = os.path.join(root, subdirectory)
            for file in os.listdir(folders):                
                # print(file)  
                if json_processed(file):
                    print(f"{subdirectory} -- {file}")                    
                    count += 1
                    shutil.rmtree(os.path.join(root, subdirectory)) 
        #         break
        #     break
        # break            
    print(count)     
       
# def batch_files_missing_database(count=0):
#     try:
#         source = upload = f"/home/ubuntu/batch-files"    
#         for root, subdirectories, files in os.walk(source):
#             for subdirectory in subdirectories:
#                 folders = os.path.join(root, subdirectory)
#                 for file in os.listdir(folders):  
#                     if not missing_in_database(file):                        
#                         account, year, month = file_info(file)        
#                         data = account_no_special(account, year)
#                         if data and not data[7]:
#                             print(f"{subdirectory} -- {file}")
#                             count += 1
#                             shutil.rmtree(os.path.join(root, subdirectory))                                
            
#     except:
#         pass
    
#     print(count)
    
def batch_files_missing_database(count=0):
    try:
        source = upload = f"/home/ubuntu/batch-files"    
        for root, subdirectories, files in os.walk(source):
            for subdirectory in subdirectories:
                folders = os.path.join(root, subdirectory)
                for file in os.listdir(folders):  
                    if not missing_in_database(file):                        
                        account, year, month = file_info(file)        
                        data = account_no_special(account, year)
                        if data and data[7]:
                            print(f"{subdirectory} -- {file}")
                            # print(data)
                            count += 1
                            shutil.rmtree(os.path.join(root, subdirectory))                                
            
    except:
        pass
    
    print(count)
    
def batch_files(count=0, row=0):
    try:
        source = upload = f"/home/ubuntu/batch-files"    
        for root, subdirectories, files in os.walk(source):
            for subdirectory in subdirectories:
                folders = os.path.join(root, subdirectory)
                for file in os.listdir(folders):
                    sheet1.write(row, 0, subdirectory)
                    sheet1.write(row, 1, file)
                    row += 1  
                    print(f"{subdirectory} -- {file}")                     
                    count += 1
    except:
        pass
    
    wb.save(f'/home/ubuntu/Clients/.Autopopulate/batch_files.xls')
    print(count)
    

def iterate_import_exceptions(count=0):
    try:
        source = upload = f"/home/ubuntu/import-exceptions"    
        for root, subdirectories, files in os.walk(source):
            for subdirectory in subdirectories:
                folders = os.path.join(root, subdirectory)
                for file in os.listdir(folders):
                    print(file)
                   
    except:
        pass
    

if __name__ == '__main__':
    # batch_files_json_exists() 
    iterate_import_exceptions()