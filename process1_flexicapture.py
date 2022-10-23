from imports import *

## tested on 10/22/2022 - uploads files to flexicapture
def upload_to_flexi(source, file, new_filename, data, year, month):
    upload = f"/home/ubuntu/flexicapture-uploads"
    try:
        print(f"Uploaded to FlexiCapture: {new_filename}")
        print()
        flexicapture_database(data, new_filename, month, year)
        send_to_endpoint(source, new_filename, data, month, year, 'statements/', 'statements')
        shutil.move(os.path.join(source, file), (os.path.join(upload, new_filename)))  
    except Exception as error:  
        pass              
    
## tested on 10/22/2022 - AssetMark holdings uploads
def flexicapture_assetmark(bankname, source, month, year, count=0):
    try:
        for file in os.listdir(source):
            if (file.endswith('.pdf') or file.endswith('.PDF')):
                account = file.split(' ')[1].split('-')[0]                         
                data = account_no_special(account, year)
                csv_file = f"{file[:-4]}.csv"
                if data and to_upload(data) and not (record_exists(data, file)) and os.path.exists(os.path.join(source, csv_file)):
                    statements = main(f"{source}/{file}", "Asset Mark Combined Holdings")
                    PDF_statement = PdfFileReader(f'{source}/{file}', strict=False)
                    for x in statements:
                        pdf_writer(f"{source}/holdings", file, PDF_statement, x['page'] ) 
                        upload_to_flexi(f"{source}/holdings", file, file, data, year, month) 
                        send_to_endpoint(source, csv_file, data, month, year, 'transactions/', 'transactions')                       
                        count += 1                  
        # uploaded_to_flexi('tkorpal@gpwa.com', f"{bankname} {month} {year}", count)
        # uploaded_to_flexi('aandersen@gpwa.com', f"{bankname} {month} {year}", count)        
    except:
        pass        


## tested on 10/22/2022 -- main flexi upload code
def flexicapture_uploads(bankname, source, month, year, count=0):
    # try:
        for file in os.listdir(source):  
            # print(file)          
            if (file.endswith('.pdf') or file.endswith('.PDF')):                        
                account = file.split(' ')[1].split('-')[0]                         
                data = account_no_special(account, year)
                # print(data)
                if data and to_upload(data) and not (record_exists(data, file)) and os.path.exists(os.path.join(source, file)):
                    load_to_flexi(source, file, file, data, year, month)
                    count += 1              
        # uploaded_to_flexi('tkorpal@gpwa.com', f"{bankname} {month} {year}", count)
        # uploaded_to_flexi('aandersen@gpwa.com', f"{bankname} {month} {year}", count)
    # except Exception as error:
    #     print(error.args)
    
## tested on 10/22/2022 - checks error folder and uploaded files to AutoPop
def errors_transactions():
    folders = ('holdings_errors', 'transactions_errors')
    source = f'/home/ubuntu/Clients/.Autopopulate'
    try:
        for folder in folders:
            print(folder)
            for file in os.listdir(os.path.join(source, folder)):            
                account = file.split(' ')[1].split('-')[0]
                year = file[:4]                                     
                data = account_no_special(account, year) 
                print(data)
                if folder == 'transactions_errors':            
                    errors_to_endpoint(os.path.join(source, folder), file, data, 'transactions/', 'transactions')
                else:
                    errors_to_endpoint(os.path.join(source, folder), file, data, 'holdings/', 'holdings')                
         
    except Exception as error:
        print(error.args)

## no longer being used -- using flexicapture_uploads
## tested on 06/21/2020 - checks if file exists in source folder - uploaded to FlexiCapture  ##
## create record in database ##
def upload_to_flexicapture(source, file, new_filename, data, month, year):
    '''
    * Only uploads if FlexiCapture box is checked on main banking recored in CRM and
      the record DOES NOT exist in the database
    * Uploads PDF to FlexiCapture
    * Uploads PDF to Endpoint - statements/
    * Updates field 'flexicapture' in database with date PDF was uploaded
    * Updates field 'statements' in database with date PDF was uploaded    
    '''
    if to_upload(data) and not (record_exists(data, new_filename)):        
        upload = f"/home/ubuntu/flexicapture-uploads"        
        if os.path.exists(os.path.join(source, file)):
            try:
                print(f"Uploaded to FlexiCapture: {new_filename}")
                print()
                flexicapture_database(data, new_filename, month, year)
                send_to_endpoint(f"{source}/{year}/{month}", new_filename, data, month, year, 'statements/', 'statements')
                shutil.move(os.path.join(source, file), (os.path.join(upload, new_filename)))    
                                                     
            except Exception as error:  
                pass 
             
    else:
        print(f"Record Exists or FlexiCapture Box not checked: {new_filename}")
        print()
        
        
def assetmark_to_flexicapture():
    upload = f"/home/ubuntu/flexicapture-uploads"
    'E11899D9-EFEB-DD11-924D-00221912ADEF'
    pass

## Manually uploading to FlexiCapture ###
######################################################################################################################################

def manually_upload_to_flexicapture(source, file, new_filename, data, month, year):
    '''
    * Only uploads if FlexiCapture box is checked on main banking recored in CRM and
      the record DOES NOT exist in the database
    * Uploads PDF to FlexiCapture
    * Uploads PDF to Endpoint - statements/
    * Updates field 'flexicapture' in database with date PDF was uploaded
    * Updates field 'statements' in database with date PDF was uploaded    
    '''
    # if not (record_exists(data, new_filename)):
    if to_upload(data) and not (record_exists(data, new_filename)):                  
        upload = f"/home/ubuntu/flexicapture-uploads"
        if (file.endswith('.pdf') or file.endswith('.PDF')):            
            if os.path.exists(os.path.join(source, file)):                 
                try:
                    print(data)
                    print(f"Uploaded to FlexiCapture: {new_filename}")                    
                    print()
                    flexicapture_database(data, new_filename, month, year)
                    send_to_endpoint(source, new_filename, data, month, year, 'statements/', 'statements')
                    shutil.move(os.path.join(source, file), (os.path.join(upload, new_filename)))                                         
                except Exception as error:  
                    pass 
                
                return True 
    return False
    # else:        
    #     print(f"Record Exists or FlexiCapture Box not checked: {new_filename}")
    #     print()

banknames = {   
                'Truist Bank' : 'Truist',                 
                "U.S. Bank, N.A." : 'US Bank',                 
                'Fifth Third Bank' : 'Fifth Third Bank',
                "First Midwest Bank" : 'First Midwest', 
                'UMB Corporate Trust Services' : 'UMB Bank',
                'Raymond James Financial Services, Inc.' : 'Raymond James',
                'BOK Financial, N.A.' : 'BOK Financial -Bank of Oklahoma Financial',                
            }

### checking Postgres database - send back up to flexicapture ### 
def send_to_flexicapture(count = 0):
    query = processed_check()
    for x in query:         
        data = get_bankstatement_info(x[5], x[4])
        if to_upload(data):
            source = f"{data[2]}Custodial_Bank Statements/{banknames[x[1]]}/Banking/{x[4]}/{x[3]}" 
            print(data)
            print(f"{source}/{x[2]}")
            if os.path.exists(f"{source}/{x[2]}"):
                upload = f"/home/ubuntu/flexicapture-uploads"
                try:
                    print(f"Uploaded to FlexiCapture: {x[2]}")
                    print(data)
                    flexicapture_database(data, x[2], x[3], x[4])
                    send_to_endpoint(source, x[2], data, x[3], x[4], 'statements/', 'flexicapture')
                    send_to_endpoint(source, x[2], data,  x[3], x[4], 'statements/', 'statements')
                    shutil.move(os.path.join(source, x[2]), (os.path.join(upload, x[2])))                                         
                except Exception as error:  
                    pass 
                break
                
            break
        else:
            count +=1
            delete_filename(x[2])            
            print(data)       
            break
    
    print(count)      
    
'''
-- Rayond James 7B5F4757-CB22-E211-969B-782BCB14085F
-- UMB 93D0C0F1-80AF-DD11-907E-001AA0C8FB71
-- BOK 0E8F3927-258D-E311-ACA0-782BCB14085F
-- Fifth Third 0AD0C0F1-80AF-DD11-907E-001AA0C8FB71
-- Truist CBEF69F2-379F-EC11-B842-0050569CCC36
-- US Bank 98D0C0F1-80AF-DD11-907E-001AA0C8FB71
-- AssetMark E11899D9-EFEB-DD11-924D-00221912ADEF
'''    

##### Flexi issues and no issues ###
bank = 'US Bank'
bank_id = '98D0C0F1-80AF-DD11-907E-001AA0C8FB71'
month = '05'
year = '2022'
   
def flexi_issues(count=0):   
    source = f'/home/ubuntu/Clients/Custodial_Bank Statements/{bank}/banking/{year}/{month}'
    data = get_flexi_issues(bank_id, month, year)
    for x in data:
        if os.path.exists(os.path.join(source, x[2])):
            shutil.copy(os.path.join(source, x[2]), (os.path.join(f"{source}/Flexi_issues", x[2])))
            print(x[2])
            count += 1
        # break
    print(count) 
    
def flexi_no_issues(count=0):    
    source = f'/home/ubuntu/Clients/Custodial_Bank Statements/{bank}/banking/{year}/{month}'
    data = no_flexi_issues(bank_id, month, year)
    for x in data:
        if os.path.exists(os.path.join(source, x[2])):
            shutil.copy(os.path.join(source, x[2]), (os.path.join(f"{source}/Flexi_no_issues", x[2])))
            print(x[2])
            count += 1
        # break
    print(count) 
 
 
     
if __name__ == '__main__':
    bank = 'AssetMark' 
    year = '2021'
    month = '12'
    source = f'/home/ubuntu/Clients/Custodial_Bank Statements/{bank}/banking/{year}/{month}/holdings/'
    for file in os.listdir(source):
        if (file.endswith('.pdf') or file.endswith('.PDF')):
            data = account_no_special(file.split(' ')[1].split('-')[0], year)             
            manually_upload_to_flexicapture(source, file, file, data, month, year)
             
    # bank = 'BOK Financial -Bank of Oklahoma Financial'
    # years = ('2022',)
    # months = ('01','02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
    # for year in years:
    #     for month in months:
    #         source = f'/home/ubuntu/Clients/Custodial_Bank Statements/{bank}/banking/{year}/{month}'   
    #         for file in os.listdir(source):
    #             if (file.endswith('.pdf') or file.endswith('.PDF')):
    #                 print(file)
    #                 try:      
    #                     data = account_no_special(file.split(' ')[1].split('-')[0], year)
    #                     # print(data)
    #                     if data:                                  
    #                         manually_upload_to_flexicapture(source, file, file, data, month, year)
    #                     # break
    #                 except IndexError:
    #                     pass
             
  