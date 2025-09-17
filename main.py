#!/usr/bin/env python3

import json
import requests
import random
import time
import sys
from requests.auth import HTTPBasicAuth
from getpass import getpass

import urllib3
urllib3.disable_warnings()

wlc9800 = input(f"WLC address: ")
user = input("User: ")
password = getpass()
auth = HTTPBasicAuth(user, password)

while True:
    try: 
        print("What percentage of AP do you want to restart?") 
        print("Choice available:") 
        print("5") 
        print("10") 
        print("25") 
        
        pourcentage = int(input("Your choice: ")) 
        match pourcentage : 
            case 5: 
                break 
            case 10: 
                break 
            case 25: 
                break 
            case _: 
                print("Invalid choice, please select a valid percentage:\n") 
    
    except: 
        print("This is not a valid percentage.\n")

headers={ 
    "Accept" : "application/yang-data+json" 
    }

print("Getting APs...")

response = requests.get(f"https://{wlc9800}/restconf/data/Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/ap-name-mac-map", headers=headers, auth=auth, verify=False)
data = json.loads(response.text)

if response.status_code != 200: 
    sys.exit("Incorrect password, script stopped")

# Store all AP name and print them
ap_mac_list = [item['wtp-mac'] for item in data['Cisco-IOS-XE-wireless-access-point-oper:ap-name-mac-map']]

nbr_ap_reboot=int(len(ap_mac_list)*(pourcentage/100))

print(f"\nNumber of AP to restart : {len(ap_mac_list)}") 

while ap_mac_list:
    print(f"\nReboot of {nbr_ap_reboot} APs :")
    # Randomly take x% of APs to reboot
    temp_ap_list=random.sample(ap_mac_list, k=nbr_ap_reboot) 
    
    # Reboot APs here 
    for item in temp_ap_list: 
        postheaders={ 
            "Content-Type" : "application/yang-data+json", 
            "Accept" : "application/yang-data+json" 
            } 
        
        postpayload = { 
            "ap-reset": [
                 {
                    "mac-addr": item 
                } 
                ] 
            }
        response = requests.post(f"https://{wlc9800}/restconf/operations/Cisco-IOS-XE-wireless-access-point-cmd-rpc:ap-reset", data=json.dumps(postpayload), headers=postheaders, auth=auth, verify=False)
        
    # Waiting before switching to another set of APs
    print(f"Waiting for at least 80% of the {nbr_ap_reboot} APs to reboot...")
    nbr_ap_up = 0 
    
    # Saving the original list to reduce the global list after processing
    temp_ap_list_save = temp_ap_list[:]
    
    while nbr_ap_up < nbr_ap_reboot*0.8:
        for mac in temp_ap_list[:]: 
            response = requests.get(f"https://{wlc9800}/restconf/data/Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/capwap-data={mac}/ap-state/ap-admin-state", headers=headers, auth=auth, verify=False)
            
            if response.status_code == 200: 
                temp_ap_list.remove(mac) 
                nbr_ap_up += 1 
                print(f"{nbr_ap_up}/{(nbr_ap_reboot*0.8)}")
            
            print("30-second wait...")
            time.sleep(30) 
    
    # Removal of APs already restarted from the list
    ap_mac_list = [x for x in ap_mac_list if x not in set(temp_ap_list_save)]
    
    # Reduction in the number of AP to restart when there are too few left 
    if ap_mac_list and len(ap_mac_list) < nbr_ap_reboot:
        nbr_ap_reboot = int(len(ap_mac_list)) 
    
    print(f"\nThere are {len(ap_mac_list)} APs left to restart")

print("\nAll APs have been restarted.")