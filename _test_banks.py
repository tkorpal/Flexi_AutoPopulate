from imports import *
from process1_flexicapture import upload_to_flexi

def test_banks(count=0):
    source = f'/home/ubuntu/Clients/.Autopopulate/TEST BANKS'
    upload = f"/home/ubuntu/flexicapture-uploads"
    try:
        for file in os.listdir(source): 
            if (file.endswith('.pdf') or file.endswith('.PDF')):     
                print(file)        
                year = file[:4]   
                month =  file[4:7]                
                account = file.split('-')[0].split(' ')[1] 
                data = account_no_special(account, year)
                if data and data[7] and not (record_exists(data, file)) and os.path.exists(os.path.join(source, file)):
                    print(data)
                    upload_to_flexi(source, file, file, data, year, month) 
                    count +=1  
                os.remove(os.path.join(source,file))
                # break           
        # uploaded_to_flexi('tkorpal@gpwa.com', f"TEST - {bankname} {month} {year}", count)
        
    except Exception as error:
        print(error.args)
    
if __name__ == '__main__':
    test_banks()