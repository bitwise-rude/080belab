#!/bin/bash

# -----------------------------------
# LOGIC FOR CITPC CONNECTOR
# written by - Meyan Adhikari
# -----------------------------------

USERNAME="080bel042"
PASSWORD="2123-2470"

# NOW LEAVE 

LOGIN_URL="https://10.100.1.1:8090/login.xml"

TIMESTAMP=$(date +%s%3N)

USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

RESPONSE=$(curl -sk --max-time 10 \
  -A "$USER_AGENT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: https://10.100.1.1:8090/" \
  --data "mode=191&username=$USERNAME&password=$PASSWORD&a=$TIMESTAMP&producttype=none" \
  "$LOGIN_URL"
)

if echo "$RESPONSE" | grep -q "You are signed in as"; then
    echo "Congrats! The process is successful, You are successfully logged in!"
else
    echo "$RESPONSE"
    echo "Hm! It seems like your credentials were wrong or you reached the maximum login limit."
fi
