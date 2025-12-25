# CITPC Auto Login Tool (Python & Bash)

A simple script to automatically log in to the CITPC / college network captive portal without opening a browser.

This tool sends the same request your browser sends when you log in manually.

## Features

- Auto login to CITPC network

- Works without opening a browser

- Python version (cross-platform)

- Bash version (Linux / WSL / Termux)

- Fast and lightweight

- No GUI required

## Requirements

- Python Version
- Python 3.x
- requests library

## Install dependency:

`pip install -r requirements.txt`

## Bash Version

> Linux / WSL / Termux


# Usage

1. Edit credentials

Open citpc_login.py and change:

username = 'YOUR_USERNAME'
password = 'YOUR_PASSWORD'

2. Run the script
python3 citpc_login.py

3. Expected output
Congrats! The process is successful, You are successfully logged in!

Bash Version Usage (Linux)

1. Edit credentials

Open citpc_login.sh and change:

USERNAME="YOUR_USERNAME"
PASSWORD="YOUR_PASSWORD"

2. Give execute permission (one time)
chmod +x citpc_login.sh

3. Run the script
./citpc_login.sh

