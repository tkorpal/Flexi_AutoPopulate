from imports import *

# Workbook is created
wb = Workbook()
  
# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Sheet 1')

def processed_schedule_d(row=0):    
    statements = scheduled_statements()     
    for x in statements:        
        account, year, month = file_info(x[2])
        data = account_no_special(account, year) 
        if data:
            destination = check_folder(data, year, account)
            filename = f"{x[2].split(' ')[0]}_{x[2].split(' ')[1]}"
            error_code = schedule_d(filename, data, x[2], destination) 
            if error_code == 200:
                print(filename)           
            # if error_code != 200:
            #     sheet1.write(row, 0, filename)
            #     sheet1.write(row, 1, data[4])
            #     sheet1.write(row, 2, error_code)
            #     row += 1
            #     print(f"{row} {filename} {error_code}")
        
    
    wb.save(f'/home/ubuntu/Clients/.Autopopulate/ScheduleD_errors.xls')