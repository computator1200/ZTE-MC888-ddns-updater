# This was the script I made first to probe around

import requests
import hashlib
import dotenv
import os

dotenv.load_dotenv()

username = os.getenv("ROUTER_ADMIN_USERNAME")
password = os.getenv("ROUTER_ADMIN_PASSWORD")

# Referer header needed for CSRF / anti-hotlink
headers = {
    "Referer": "http://192.168.0.1/"
}

params = {
    "cmd": "LD",
    "isTest": "false"
}

response = requests.get('http://192.168.0.1/goform/goform_get_cmd_process', 
                        params=params,
                        headers=headers
                        )

LD = response.json()['LD']

session = requests.Session()
print("Cookies from first GET request: ", session.cookies)

hashed_password = hashlib.sha256((hashlib.sha256(f"{password}".encode(encoding="utf-8")).hexdigest().upper() + LD).encode(encoding="utf-8")).hexdigest().upper()

params = {
    "goformId": "LOGIN",
    "isTest": "false"
}

body = {
    "user": username,
    "password": hashed_password
}

response = session.post('http://192.168.0.1/goform/goform_set_cmd_process', 
                        params=params,
                        headers=headers,
                        data=body
                        )

print("Response from first POST request: ", response.text)
print("Cookies after the POST request: ", session.cookies)

params = {
    "cmd": "getddns_status" # This is the main check
}

response = session.get('http://192.168.0.1/goform/goform_get_cmd_process', 
                        params=params,
                        headers=headers
                        )

print("Response from second GET request: ", response.text)

# If not applied it returns: {'getddns_status':'4'}

# Now analyze the javascript

response = session.get('http://192.168.0.1/js/adm/ddns_settings.js')
with open("ddns_settings.js", "w", encoding="utf-8") as file:
    file.write(response.text)


response = session.get('http://192.168.0.1/js/service.js')
with open("service.js", "w", encoding="utf-8") as file:
    file.write(response.text)

# At this point the rest of the logic is simple, check is the status code is 4, hit the apply route, skip if it's not 4.
# I'll be copying over this code into main.py