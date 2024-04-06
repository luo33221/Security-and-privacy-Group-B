#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 00:18:58 2023

@author: ericwei
"""

from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
import pandas as pd
import mysql.connector


app = Flask(__name__)
Bootstrap(app)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "000000",  # Replace with your root password
    "database": "smarthospital",
}



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            return redirect(url_for('data'))
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error), 401
    return render_template('login.html', error=error)


def validate_user(username, password):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT * FROM user WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    connection.close()
    return user is not None


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if username or email is already taken
        if is_username_taken(username):
            error = 'Username already exists. Please choose another username.'
        elif is_email_taken(email):
            error = 'Email already registered. Please use another email.'
        else:
            add_user(username, password, email)
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

def is_email_taken(email):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT * FROM user WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    connection.close()
    return user is not None

def is_username_taken(username):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT * FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    connection.close()
    return user is not None


def add_user(username, password, email):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "INSERT INTO user (username, password, email) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, password, email))
    connection.commit()
    connection.close()

'''
@app.route('/data', methods=['GET'])
def data():
    # Connect to the MySQL server
    connection = mysql.connector.connect(**db_config)

    # Fetch data from the case table
    query = "SELECT * FROM case;"
    df  = pd.read_sql_query(query, connection)

    # Close the connection to the MySQL server
    connection.close()

    # Pass the DataFrame to the template
    return render_template('data.html', data=df)
'''

@app.route('/data', methods=['GET'])
def data():
    # Connect to the MySQL server
    connection = mysql.connector.connect(**db_config)

    # Fetch data from the case table
    query_data = "SELECT * FROM medicalcase;"
    df_data = pd.read_sql_query(query_data, connection)

    # Fetch data from the user table
    query_user = "SELECT * FROM user;"
    df_user = pd.read_sql_query(query_user, connection)

    # Close the connection to the MySQL server
    connection.close()

    # Pass the DataFrames to the template
    return render_template('data.html', data=df_data, userdata=df_user)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    safe_query = f"%{query}%"

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query_string = f"SELECT * FROM medicalcase WHERE diagnosis LIKE %s;"
    cursor.execute(query_string, (safe_query,))

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    connection.close()

    return render_template('search.html', data=rows, columns=columns)


@app.route('/add', methods=['GET', 'POST'])
def add_data():
    # Connect to the MySQL server
    connection = mysql.connector.connect(**db_config)

    if request.method == 'POST':
        # Get the data from the form
        patientname = request.form['patientname']
        age = request.form['age']
        gender = request.form['gender']
        doctor = request.form['doctor']
        illness = request.form['illness']
        diagnosis = request.form['diagnosis']

    

        # Insert the data into the case table
        query = "INSERT INTO medicalcase (patientname, age, gender, doctor, illness, diagnosis) VALUES (%s, %s, %s, %s, %s, %s);"
        cursor = connection.cursor()
        cursor.execute(query, (patientname, age, gender, doctor, illness, diagnosis))

        # Commit the transaction
        connection.commit()

    # Fetch data from the case table
    df_data = pd.read_sql_query("SELECT * FROM medicalcase;", connection)
    df_user = pd.read_sql_query("SELECT * FROM user;", connection)
    # Close the connection to the MySQL server
    connection.close()

    # Pass the DataFrame to the template
    return render_template('data.html', data=df_data, userdata=df_user)

        
        

@app.route('/delete', methods=['POST'])
def delete_data():
    data_id = request.form['data_id']

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM medicalcase WHERE id = %s;", (data_id,))

    connection.commit()
    connection.close()

    update_ids()

    return redirect(url_for('data'))

def update_ids():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM medicalcase ORDER BY id;")

    id_list = [row[0] for row in cursor.fetchall()]
    updated_id_list = list(range(1, len(id_list) + 1))

    for old_id, new_id in zip(id_list, updated_id_list):
        cursor.execute("UPDATE medicalcase SET id = %s WHERE id = %s;", (new_id, old_id))

    connection.commit()
    connection.close()
    
    

def get_columns_names():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SHOW COLUMNS FROM medicalcase;")
    columns = [column[0] for column in cursor.fetchall()]
    connection.close()
    return columns

@app.route('/update', methods=['POST'])
def update_data():
    data = request.get_json()
    data_id = data['id']
    column_index = int(data['column'])
    new_value = data['value']

    columns = get_columns_names()
    column_name = columns[column_index]

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"SELECT {column_name} FROM medicalcase WHERE id = %s;", (data_id,))
    old_row = cursor.fetchone()

    if old_row is not None:
        old_value = old_row[0]
    else:
        connection.close()
        return jsonify({'error': 'Row not found', 'oldValue': None})

    cursor.execute(f"UPDATE medicalcase SET {column_name} = %s WHERE id = %s;", (new_value, data_id))

    connection.commit()
    connection.close()
    return jsonify({})







if __name__ == '__main__':
    app.run(debug=True)


