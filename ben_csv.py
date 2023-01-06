from imports import *

holdings = f"/home/ubuntu/Clients/.Autopopulate/Ben_ Comerica_CSV/holdings"
transactions = f"/home/ubuntu/Clients/.Autopopulate/Ben_ Comerica_CSV/transactions"

def comerica_csv():
    try:
        for file in os.listdir(holdings): 
            if (file.endswith('.csv') or file.endswith('.CSV')):
                year = file[:4]   
                month =  file[4:7]                
                account = file.split('-')[0].split(' ')[1] 
                pdf_file = json_file = f"{file.split('.')[0]}.pdf"
                data = account_no_special(account, year)
                if data and not record_exists(data, pdf_file):
                    flexicapture_database(data, pdf_file, month, year)
                    print('Sending to Holdings')
                    send_to_endpoint(holdings, file, data, month, year, 'holdings/', 'holdings')
                    if os.path.exists(os.path.join(transactions, file)):
                        print("Sending to Transactions")
                        send_to_endpoint(transactions, file, data, month, year, 'transactions/', 'transactions')
                        
        # for file in os.listdir(transactions): 
        #     if (file.endswith('.csv') or file.endswith('.CSV')):
        #         year = file[:4]   
        #         month =  file[4:7]                
        #         account = file.split('-')[0].split(' ')[1] 
        #         pdf_file = json_file = f"{file.split('.')[0]}.pdf"
        #         data = account_no_special(account, year)
        #         if data:                     
        #             send_to_endpoint(transactions, file, data, month, year, 'transactions/', 'transactions')
                    
              
        
    except Exception as error:
        print(f"Main Error: {error.args}")
        
if __name__ == '__main__':
    comerica_csv()