import requests
import base64
import os
import io
import json
from DTauthenticator  import *
from DTaddresses import DEFAULT_POD_LOCATION
from PIL import Image

NO_OBLIGATION= "< Unrestricted >"
DIR_PATH = os.path.abspath(os.path.dirname(__file__))
pod_types = (NO_OBLIGATION, "Financial", 'Social','Medical')
DEFAULT_POD_LOCATION = DEFAULT_POD_LOCATION + '/' if DEFAULT_POD_LOCATION[-1] != '/' else DEFAULT_POD_LOCATION



def callAPI(url,resource_path,sub_id, claim):

    ip_location_details = DTauthenticator.get_location(DTauthenticator)
    print(ip_location_details)
    if (ip_location_details is None):
        return ip_location_details
    current_time = DTauthenticator.get_timezone_based_timestamp(DTauthenticator,ip_location_details['timezone'])
    time_rounded = DTauthenticator.rounded_to_the_last_5th_minute_epoch(DTauthenticator,int(current_time.timestamp()))
    auth_token = DTauthenticator.encode_for_header(DTauthenticator, resource_path , str(time_rounded))

    files=(
        ('auth_token', (None, auth_token.signature.hex())),
        ('claim', (None, claim)),
        ('id_subscription', (None, sub_id)),
    )    

    try:
        response = requests.post(url, files = files)
        if(response.status_code == 200):
            extension = url.split(".")[-1]
            data = response.content.decode("utf-8")
            data = json.loads(data)
            decoded_image_bytes = base64.b64decode(data['resource']['base64_encoded_image'])
            image_stream = io.BytesIO(decoded_image_bytes)
            file_path = os.path.abspath(os.path.join(DIR_PATH,"../../"))+"/Response."+extension
            print(file_path)
            image = Image.open(image_stream)
            image.save(file_path)
            return ("Response."+extension)                  #returning image path instead of image data
        else:
            print("API Call Failed")
            return response
    except Exception as e:
            print(f"An error occurred: {e}") 
            return None

def readFileData(file_path):
    try:
        file_exist=os.path.exists(file_path)
        if file_exist:
                    fp = open(file_path, 'r')
                    data = json.load(fp)
                    fp.close()
                    return data
        else :
            print("File "+file_path+ " Doesn't Exist")
            return None
    except OSError:
            return None

def updateFileData(new_data, file_path):
    try:
        file_exist=os.path.exists(file_path)
        if file_exist:
            with open(file_path, "w") as outfile:
                json.dump(new_data,outfile)
        else :
            print("File "+file_path+ " Doesn't Exist")
            return None
    except OSError:
            return None
    
def get_time_string(seconds):
    seconds = int(seconds)
    days = seconds // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    time_string = f"{days}d {hours}hr {minutes}m {remaining_seconds}s"
    return time_string

def get_obligations(default_pod_obligations,res_obligations,type,api=False):
    country_list= readFileData(os.path.abspath(os.path.join(DIR_PATH,"../../node/assets/files/countries.json")))
    country_names=country_list['countries']
    return_object = {"value":"Unrestricted", "pod_default_value":True}
    if res_obligations['obligations']!={} and type in res_obligations['obligations'].keys():
        return_object = {"value":res_obligations['obligations'][type], "pod_default_value":False}
    elif default_pod_obligations['default']!={} and type in default_pod_obligations['default'].keys():
        return_object =  {"value":default_pod_obligations['default'][type], "pod_default_value":True}
    if return_object['value'] == 'Unrestricted':
        return return_object
    else:
        if api: 
            if type == "temporal":
                return_object['timestamp'] = (return_object['value'])
                return_object['value'] = get_time_string(return_object['value'])
            elif type == 'domain':
                return_object['value'] = (return_object['value'])
                return_object['name'] = pod_types[(return_object['value'])+1]
            elif type == 'country':
                return_object['value'] = (return_object['value'])
                return_object['name'] = country_names[(return_object['value'])]
                return_object['country_code'] = country_list['list'][return_object['value']]['code']
            
        else:
            if type == "temporal":
                return_object['value'] = get_time_string(return_object['value'])
            elif type == 'domain':
                return_object['value'] = pod_types[(return_object['value'])+1]
            elif type == 'country':
                return_object['value'] = country_names[(return_object['value'])]
    return return_object 

def get_obligation_by_res_path(path):
    return_object = {}
    pod_id = path.split('/')[1]
    res_obligations=  readFileData(DEFAULT_POD_LOCATION + pod_id + "/DTconfig.json")
    default_pod_obligations=  readFileData(DEFAULT_POD_LOCATION + pod_id + "/DTobligations.json")
    res_id = None
    for res in res_obligations['resources']:
         if path in  res_obligations['resources'][res]['url']: # finds resource id by comparing path with url
              res_id=res    
    for policy in ['access_counter','temporal','domain','country']:
        return_object[policy] = get_obligations(default_pod_obligations,res_obligations['resources'][res_id],policy,True)
    print(return_object)
    return return_object
