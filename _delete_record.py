from imports import *
import sys

if __name__ == "__main__": 
    for i, arg in enumerate(sys.argv):
        delete_filename(arg)
        print(arg)
 
# for i in range()    
# for i in range(1, worksheet.max_row): 
#     if worksheet.cell(row=i, column=3).value:
#         print(worksheet.cell(row=i, column=3).value)
#         delete_filename(worksheet.cell(row=i, column=3).value)
        
        
        
 