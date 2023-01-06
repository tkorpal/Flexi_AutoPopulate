import os
import re
import sys
import requests
from pathlib import Path
from werkzeug.utils import secure_filename


user = os.environ.get('request_user')  
password = os.environ.get('request_password')  

sys.path.append('/home/ubuntu/ProcessingSite/Schedule_D')
from postgres_updates import update_database

base_url = 'https://autopopulate.azurewebsites.net'

def send_request(resource, file):
    url = f"{base_url}/api/v1/{resource}"    
    r = requests.post(url,auth=(user, password), files={'file': open(file, 'rb')}) 
    print(f"Send Request Status Code: {r.status_code}")    
    return r.status_code

def get_statement_id(filename):    
    return Path(secure_filename(filename)).stem

def schedule_d(statement_name, data, file, destination, return_unmapped=False):
    statement_id = get_statement_id(statement_name)
    url = f"{base_url}/api/v1/statements/{statement_id}/scheduled"
    if return_unmapped:
        url += "?returnUnmapped=true"
    response = requests.get(url, auth=(user, password))    
    if response.status_code == 200:
        print(statement_name) 
        print(data)
        content_disposition = response.headers["content-disposition"]
        filename = re.findall('filename="(.+)"', content_disposition)[0]        
        with Path(f"{destination}/{filename}").open("wb") as f:
            f.write(response.content)
        update_database(data, file, 'Processed')
        return response.status_code
    else:
        return response.status_code
         
