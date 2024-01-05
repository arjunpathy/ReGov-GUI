from web3 import Web3
from DTindexing_oracle import DTindexing_oracle
import os
import json
from DTaddresses import WEBPROVIDER,DTINDEXING
from DTutilities import *
from DTaddress_generator import DTaccount_generator

from DTsubscription_oracle import DTsubscription_oracle
# Connect to a local EthereFum node
keys = DTaccount_generator.generate_account()
public_key = keys[0]
private_key = keys[1] 

try:
    web3 = Web3(Web3.WebsocketProvider(WEBPROVIDER))
    web3.eth.default_account =  web3.eth.accounts[0]
except Exception as e:
    print(f"An error occurred: {e}")

# Event handler function for button click
def register_pod(pod_reference, pod_type, public_key, private_key):
    # Call the Solidity function
    pod_location=pod_reference
    
    ref = bytes(pod_reference, 'utf-8')
    print(ref)
    print(pod_type,public_key,private_key)

    try:
        indexing_oracle=DTindexing_oracle(DTINDEXING,private_key)
        id,public_key_pod,private_key_pod,obligation_address = indexing_oracle.register_Pod(ref,pod_type,public_key,private_key)
        generate_config_files(pod_location,id,public_key_pod,public_key,private_key_pod,obligation_address)
        print("Pod Created. Pod Id : "+ str(id))
        return { "id":str(id), "message" : None}
    except Exception as e:
        print(f"An error occurred: {e}")
        return { "id":None, "message" : repr(e)}

def register_resource(pod_location,pod_id, url, sub_id, pod_access_control_array):

    ref = bytes(url, 'utf-8')
    try:
        indexing_oracle=DTindexing_oracle(DTINDEXING,private_key) 
        id = indexing_oracle.add_resource(int(pod_id), ref, int(sub_id))
        print("Resource Created. Resource Id :  "+ str(id))
        update_pod_config(pod_location,pod_id, id, url, sub_id,pod_access_control_array)
        return {"id":str(id), "message":"Resource " + str(id) + " created successfully."}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"id":None, "message":repr(e)}

def get_resource(id):
    
    try:
        indexing_oracle=DTindexing_oracle(DTINDEXING,private_key) 
        result = indexing_oracle.get_resource_by_id(int(id)) 
        print(result)
        resource = {'id': result[0], "address": result[1], "url": result[2].decode("utf-8") , "podId": result[3], "isActive": result[4]}
        return resource
        
    except Exception as e:
        print(f"An error occurred: {e}")

def get_resource_by_pod(pod_id, sub_id):
    try:
        indexing_oracle=DTindexing_oracle(DTINDEXING,private_key) 

        resources = indexing_oracle.get_resource_information(int(pod_id), int(sub_id))
        print(resources)
        return resources
    except Exception as e:
        print(f"An error occurred: {e}")

def deactivate_resource(id):
    print (id)
    try:        
        indexing_oracle=DTindexing_oracle(DTINDEXING,private_key)
        result = indexing_oracle.deactivate_resource(int(id))
        print(result)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")  

def generate_config_files(pod_location,id,address,owner,private_key,obligations_address):
    id = str(id)
    os.makedirs(os.path.dirname(pod_location+"/"+id+"/DTconfig.json"), exist_ok=True)
    with open(pod_location+"/"+id+"/DTconfig.json", 'w') as f:
        config={"id": id, "address": address, "resources": {}, "owner": owner, "private_key": private_key}
        json.dump(config, f, indent=2)
    with open(pod_location+"/"+id+"/DTobligations.json", 'w') as f2:
        obligations={"default": {},"address":obligations_address}
        json.dump(obligations, f2, indent=2)

    with open(pod_location+"/"+id+"/DTaccess_control_list.json", 'w') as f3:
        json.dump({"pub_keys": [] }, f3, indent=2)

def update_pod_config(pod_location, pod_id, id,url, sub_id,pod_access_control_array):
    
    resource = {  "id": id, "url": url, "subscription_id": int(sub_id), "obligations": {},"access_control_list":pod_access_control_array}
    print(resource)
    try:
        pod_config = readFileData(pod_location+pod_id+"/DTconfig.json")
        pod_config['resources'][id] = resource
        updateFileData(pod_config,pod_location+pod_id+"/DTconfig.json" )
    except OSError:
        return None

def get_user_address():
    return web3.eth.default_account
    