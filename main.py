import requests
from hashlib import sha256
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

hashed_password = sha256((sha256(f"{password}".encode(encoding="utf-8")).hexdigest().upper() + LD).encode(encoding="utf-8")).hexdigest().upper()

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

params = {
    "cmd": "getddns_status" # This is the main check
}

response = session.get('http://192.168.0.1/goform/goform_get_cmd_process', 
                        params=params,
                        headers=headers
                        )

ddns_status = response.json()['getddns_status']

# Helper function to required find values via cmd
def cmd(session, option):

    headers = {
        "Referer": "http://192.168.0.1/"
    }

    params = {
        "cmd" : option
    }

    response = session.get('http://192.168.0.1/goform/goform_get_cmd_process', 
                        params=params,
                        headers=headers
                        )

    return response.json()[option]



if ddns_status == '4':
    # Hit the apply route
    
    # Find the required values to send in the apply request

    DDNS = cmd(session, "DDNS")
    DDNS_Enable = cmd(session, "DDNS_Enable")
    DDNS_Mode = cmd(session, "DDNS_Mode")
    DDNSProvider = cmd(session, "DDNSProvider")
    DDNSAccount = cmd(session, "DDNSAccount")
    DDNSPassword = cmd(session, "DDNSPassword")
    DDNS_Hash_Value = cmd(session, "DDNS_Hash_Value")
    DDNSProvider_default = cmd(session, "DDNSProvider_default")

    Language = cmd(session, "Language")
    cr_version = cmd(session, "cr_version")
    wa_inner_version = cmd(session, "wa_inner_version")

    RD = cmd(session, "RD")

    version_hash = sha256(wa_inner_version.encode(encoding="utf-8") + cr_version.encode(encoding="utf-8")).hexdigest().upper()
    AD = sha256(version_hash.encode(encoding="utf-8") + RD.encode(encoding="utf-8")).hexdigest().upper()

    # Send the apply request

    params = {
        "goformId": "DDNS",
        "isTest": "false"
    }

    body = {
        'DDNS': DDNS,
        'DDNS_Enable': DDNS_Enable,
        'DDNS_Mode': DDNS_Mode,
        'DDNSProvider': DDNSProvider,
        'DDNSAccount': DDNSAccount,
        'DDNSPassword': DDNSPassword,
        'DDNS_Hash_Value': DDNS_Hash_Value,
        'AD': AD
    }

    response = session.post(url='http://192.168.0.1/goform/goform_set_cmd_process', headers=headers, params=params, data=body)

    print(response.text)