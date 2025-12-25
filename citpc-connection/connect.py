'''
LOGIC FOR CITPC CONNECTOR
    written by- Meyan Adhikari
'''

username = '080bel042' # your username 
password = '2123-2470' # your password 

# REST LEAVE IT TO THE SCRIPT 

login_url = 'https://10.100.1.1:8090/login.xml'


import requests
import time

payload = {
            'mode': '191',
            'username': username,
            'password': password,
            'a': time.time()*1000, # unneccesary
            'producttype': 'none'
        }

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://10.100.1.1:8090/'
        }

try:
    response = requests.post(login_url, data=payload, headers=headers, verify=False, timeout=10)
    if response.status_code == 200:
        if "You are signed in as" in response.text:
            print("Congrats! The process is successfull, You are succesfully logged in !")
        else:
            print(response.text)
            print("Hm! It seems like your credentials were wrong or in a non likely sceniaro you have reached your maximum login limit")

except requests.exceptions.RequestException as e:
    print(f'Unable to connect becuase of error {e}')