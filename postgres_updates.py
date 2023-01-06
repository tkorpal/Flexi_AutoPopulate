import psycopg2
from datetime import date
import os

today = date.today()

conn = psycopg2.connect(
    host = os.environ.get('azure_host'),
    database = os.environ.get('azure_database_auto'),
    user = os.environ.get('azure_user_auto'),
    password = os.environ.get('azure_password_auto')
    )           
cursor = conn.cursor()


## used temporary for batch-files 08/31/2022
def json_processed(filename):
    try:
        exists_query = """ select * from file_status where filename = %s
            and (holdings is not null or transactions is not null) """
        cursor.execute(exists_query, (filename,))
        if cursor.rowcount >= 1:
            return True
        return False 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def missing_in_database(filename):
    try:
        exists_query = """ select * from file_status where filename = %s """             
        cursor.execute(exists_query, (filename,))
        if cursor.rowcount >= 1:
            return True
        return False 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    


## checks if record exists - returns row count: 0 or 1
def record_exists(data, filename):
    try:
        exists_query = """ select * from file_status where client = %s and filename = %s """
        cursor.execute(exists_query, ( data[0], filename))
        if cursor.rowcount >= 1:
            return True
        return False 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


## test on 06/15/2022 - checks if record exists
def flexicapture_database(data, filename, month, year):
    try:
        if not record_exists(data, filename):
            query = """INSERT INTO file_status(client, filename, bankname, month, year, account, flexicapture, bank_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) """
            to_insert = (data[0], filename, data[4], month, year, data[3], today, data[6] )
            cursor.execute(query, to_insert)
            conn.commit()
        # cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


## tested on 06/21/2022 - checks if record exists
def update_database(data, filename, column):
    try:       
        if record_exists(data, filename):                        
            update_query = """ UPDATE file_status set  """+ column +"""  = %s where client = %s and filename = %s """
            cursor.execute(update_query, (today, data[0], filename))       
            conn.commit()
            print(f"Database Updated: {filename}")
        else:
            print(f"Record does not exists: {filename}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

## updates column field to null using filename ##
def update_to_null(filename, column):
    try:                        
        update_query = """ UPDATE file_status set  """+ column +"""  = NULL where filename = %s """
        cursor.execute(update_query, (filename,))       
        conn.commit()
        print(f"Database Updated -- NULL Field: {filename}")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
 
## delete record using filename ##
def delete_filename(filename):
    try:
        delete_record = """ DELETE FROM file_status WHERE filename = %s;"""
        cursor.execute(delete_record, (filename,))      
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
   
def update_csv_database(data, filename, column):
    try:
        if record_exists(data, filename):            
            update_query = """ UPDATE file_status set  """+ column +"""  = %s where client = %s and filename = %s """
            cursor.execute(update_query, (today, data[0], filename))       
            conn.commit()
        else:
            pass
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
########################################################################################################################
## check is field is null for transactions or holdings - if null returns TRUE
# def endpoint_error(data, filename, resource):
#     try:                
#         exists_query = """ select * from file_status where client = %s and filename = %s and """+ resource +""" IS NULL """
#         cursor.execute(exists_query, (data[0], filename))         
#         if cursor.rowcount >= 1:
#             return False
#         return True 
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)

# def scheduled_statements():
#     exists_query = """ select * from file_status where holdings is not null and transactions is not null and processed is null
#                         order by flexicapture DESC"""
#     cursor.execute(exists_query)
#     data = cursor.fetchall()
#     return data

def scheduled_statements():
    exists_query = """ select * from file_status where holdings = '2022-12-29' and transactions is not null and processed is null   """
    cursor.execute(exists_query)
    data = cursor.fetchall()
    return data

# def scheduled_statements():
#     exists_query = """ select * from file_status where holdings = %s and transactions is not null and processed is null """
#     cursor.execute(exists_query, ('2022-10-25',))
#     data = cursor.fetchall()
#     return data

def scheduled_bank_id():
    exists_query = """ select * from file_status where bank_id = 'D4B2E41B-427D-DE11-AC3D-00221912ADEF' """
    cursor.execute(exists_query)
    data = cursor.fetchall()
    return data
    


## checks if record exists - returns row count: 0 or 1
def test_record_exists(data, filename):
    try:
        exists_query = """ select * from file_status where client = %s and filename = %s """
        cursor.execute(exists_query, ( data, filename))
        if cursor.rowcount >= 1:
            return True
        return False 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        

    
    
#### resending backup to Flexicapture -- check if box is checked in CRM -- Schedule D Excel ##
def processed_check():
    exists_query = """ select * from file_status where holdings is null and transactions
                    is null  """
    cursor.execute(exists_query)
    data = cursor.fetchall()
    return data


    
def get_flexi_issues(bank_id, month, year):
    try:
        exists_query = """ select * from file_status where bank_id = %s and month = %s and
                        year = %s and holdings is null and transactions is null"""
        cursor.execute(exists_query, ( bank_id, month, year))
        data = cursor.fetchall()
        return data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
def no_flexi_issues(bank_id, month, year):
    try:
        exists_query = """ select * from file_status where bank_id = %s and month = %s and
                        year = %s and holdings is not null """
        cursor.execute(exists_query, ( bank_id, month, year))
        data = cursor.fetchall()
        return data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
if __name__ == '__main__':
    data = get_flexi_issues('CBEF69F2-379F-EC11-B842-0050569CCC36', '05', '2022')
    for x in data:
        print(x[2])
        break