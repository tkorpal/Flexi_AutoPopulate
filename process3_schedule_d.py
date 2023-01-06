from imports import *


# 200 - Success
# 204 - Not Mapped
# 400 - No file in request
# 404 - Statement Not Found

# Workbook is created
wb = Workbook()
wb_204 = Workbook()
  
# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Sheet 1')
sheet_204 = wb_204.add_sheet('Sheet 1')

def processed_schedule_d(row=0, error_row=0):  
    statements = scheduled_statements() 
    try:
        for x in statements:        
            account, year, month = file_info(x[2])
            data = account_no_special(account, year) 
            if data:
                destination = check_folder(data, year, account)
                filename = f"{x[2].split(' ')[0]}_{x[2].split(' ')[1]}"
                error_code = schedule_d(filename, data, x[2], destination) 
                # if error_code == 200:
                #     print(filename)           
                if error_code == 204:
                    sheet_204.write(row, 0, filename)
                    sheet_204.write(row, 1, data[4])
                    sheet_204.write(row, 2, error_code)
                    row += 1                    
                elif error_code == 400 or error_code == 404 :
                    sheet1.write(error_row, 0, filename)
                    sheet1.write(error_row, 1, data[4])
                    sheet1.write(error_row, 2, error_code)
                    error_row += 1             
                    print(f"{filename} {error_code}")
                
        
        wb_204.save(f'/home/ubuntu/Clients/.Autopopulate/Needs_Mapping.xls')
        wb.save(f'/home/ubuntu/Clients/.Autopopulate/Errors.xls')
    except Exception as error:
        print(error.args)