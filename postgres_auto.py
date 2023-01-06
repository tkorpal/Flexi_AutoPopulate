import psycopg2
from datetime import date
import os

today = date.today()

conn = psycopg2.connect(
    host = os.environ.get('azure_host'),
    database = 'autopopulate_banking',
    user = os.environ.get('azure_user_auto'),
    password = os.environ.get('azure_password_auto')
    )           
cursor = conn.cursor()

def record_exists(filename):
    try:
        exists_query = """ select * from statement where id = %s  """
        cursor.execute(exists_query, (filename,))
        # cursor.execute(exists_query, filename)
        data = cursor.fetchall()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
        
def delete_autopopulate_record(filename):
    try:
        delete_record = """ DELETE FROM statement WHERE id = %s;"""
        cursor.execute(delete_record, (filename,))      
        conn.commit()
        print(f"Deleted from database: {filename}")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
if __name__ == '__main__':
    print(delete_record('202112_347NT606-FFTReins'))
    
        
        
