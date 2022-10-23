import os
import shutil
from datetime import date
from PyPDF2 import PdfFileReader, PdfFileWriter  

today = date.today()

delete_file = lambda source, file : os.remove(os.path.join(source, file)) if os.path.exists(f"{source}/{file}") else False
create_folder = lambda folder : os.mkdir(folder) if not os.path.exists(folder) else False

move_file = lambda source, file, destination, pdf : shutil.move(os.path.join(source, file), os.path.join(destination, pdf)) \
                if os.path.exists(f"{source}/{file}") else False

## Move file to designated folder ##
file_moved = lambda source, file, destination, pdf : shutil.move(os.path.join(source, file), os.path.join(destination, pdf)) \
                if os.path.exists(f"{source}/{file}") else False  
                
copy_file = lambda source, file, destination, pdf : shutil.copy(os.path.join(source, file), os.path.join(destination, pdf)) \
                if os.path.exists(f"{source}/{file}") else False
                
def file_info(filename):
    return filename.split('-')[0].split(' ')[1], filename[:4], filename[4:6]
                
## writes file with removed pages to destination ##
def pdf_writer(destination, new_filename, PDF_statement, pages):   
    output = PdfFileWriter()
    for page in pages:                     
        output.addPage(PDF_statement.getPage(page))
        with open(f"{destination}/{new_filename}", 'wb') as f:                
            output.write(f)
        f.close()

## creates Autopopulate folder ##
def check_folder(data, year, account):
    try:
        client_folder = f"{data[2]}{data[0]}/{year}/Banking"
        destination = 'no destination available' 
        if os.path.exists(client_folder):
            # destination = 'no destination available'        
            for dir in os.listdir(client_folder):                
                if os.path.isdir(f'{client_folder}/{dir}'):                    
                    if dir.startswith(account):                        
                        destination = os.path.join(client_folder, dir)
                        break
            if not os.path.exists(os.path.join(client_folder, account)) and not os.path.exists(destination):                
                os.mkdir(os.path.join(client_folder, account)) 
                destination = os.path.join(client_folder, account)   

            create_folder(os.path.join(destination, '.Autopopulate'))

            return f"{destination}/.Autopopulate"  

        return False                 
    except Exception as error:
        print(error.args)

## check for complete folder
def check_destination(source, file, destination):
    if destination and os.path.exists(destination):    
        return True
    file_moved(source, file, '/home/ubuntu/Clients/.Autopopulate/folder_structure',  file)
    return False

## check is file returns client data ##
def check_data(source, file, data):
    if data: 
        return True
    file_moved(source, file, '/home/ubuntu/Clients/.Autopopulate/client_errors', file)
    return False