#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
import pandas as pd
import mysql.connector
import time

app = Flask(__name__)
Bootstrap(app)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "000000",  # Replace with your root password
    "database": "smarthospital",
}



# Define a dictionary to keep track of request counts per IP address
request_counts = {}

# Define a threshold for maximum requests per minute per IP address
MAX_REQUESTS_PER_MINUTE = 10

# Define a cooldown period in seconds for each IP address after exceeding the threshold
COOLDOWN_PERIOD = 30

def is_ip_blocked(ip):
    """
    Checks if an IP address is blocked due to exceeding the request limit.
    """
    if ip in request_counts:
        last_request_time = request_counts[ip]["last_request_time"]
        if time.time() - last_request_time < COOLDOWN_PERIOD:
            if request_counts[ip]["count"] >= MAX_REQUESTS_PER_MINUTE:
                print(f"Warning: IP  is blocked due to exceeding the request limit.")
                return True
    return False


@app.route('/')
def home():
    client_ip = request.remote_addr

    if is_ip_blocked(client_ip):
        return jsonify({"error": "Too many requests. Please try again later."}), 429

    # Update request count for the IP address
    if client_ip in request_counts:
        request_counts[client_ip]["count"] += 1
        request_counts[client_ip]["last_request_time"] = time.time()
    else:
        request_counts[client_ip] = {"count": 1, "last_request_time": time.time()}

    return render_template('home.html')


# Dictionary to store login attempts
login_attempts = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if there are too many login attempts from this IP
        ip_address = request.remote_addr
        if ip_address in login_attempts:
            if login_attempts[ip_address]['attempts'] >= 3:
                return render_template('login.html', error='Maximum login attempts reached. Please try again later.'), 429
        
        # Validate user credentials
        if validate_user(username, password):
            # Reset login attempts for this IP if login successful
            if ip_address in login_attempts:
                del login_attempts[ip_address]
            return redirect(url_for('data'))
        else:
            error = 'Invalid credentials. Please try again.'
            # Update login attempts for this IP
            if ip_address in login_attempts:
                login_attempts[ip_address]['attempts'] += 1
                login_attempts[ip_address]['timestamp'] = time.time()
            else:
                login_attempts[ip_address] = {'attempts': 1, 'timestamp': time.time()}
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


