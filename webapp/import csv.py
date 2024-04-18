import csv
import mysql.connector
import pandas as pd

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "000000",  
    "database": "smarthospital",
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

csv_file_path = "C:\\Users\\luomi\\Desktop\\Security-and-privacy\\webapp\\patient_data.csv"
with open(csv_file_path, "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  

    for row in csv_reader:
        insert_query = "INSERT INTO medicalcase (patientname, age, gender, doctor, illness, diagnosis) VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.execute(insert_query, row)

    connection.commit()


query = "SELECT * FROM medicalcase;"
df = pd.read_sql_query(query, connection)

connection.close()

print(df)
