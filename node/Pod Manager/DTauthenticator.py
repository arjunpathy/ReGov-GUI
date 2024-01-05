from inspect import signature
from web3 import Web3
from datetime import datetime,timedelta,time
from datetime import datetime
import pytz
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
from DTaddresses import WEBPROVIDER
from DTaddress_generator import DTaccount_generator
import requests

keys = DTaccount_generator.generate_account()
private_key = keys[1] 
"""
Class that implements the functions to authenticate HTTP requests for the resources.
"""
class DTauthenticator():
    """
    Class initializer.
    """
    def __init__(self, *args, **kw):
        self.w3=Web3(Web3.WebsocketProvider(WEBPROVIDER))

    def get_ip():
        try:
            response = requests.get('https://api64.ipify.org?format=json').json()
            return response
        except Exception as e:
            return None
    
    def get_location(self):
        try:
            response = DTauthenticator.get_ip()
            if response is not None:
                ip_address = response["ip"]
                response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
                location_data = {
                    "ip": ip_address,
                    "city": response.get("city"),
                    "region": response.get("region"),
                    "country": response.get("country_name"),
                    "country_code": response.get("country_code"),
                    "timezone": response.get("timezone")
                }
                return location_data
            else:
                print("IP Geolocation Failed! Check your internet connection.")
                return None
                # return {'city': 'Rome', 'region': 'Lazio', 'country': 'Italy','country_code':'IT','timezone': 'Europe/Rome'}
        except Exception as e:
            print(e)
            return None

    """
    Rounds the given unix epoch of 5 minutes.
    """    
    def rounded_to_the_last_5th_minute_epoch(self,unix_time):
        date_time = datetime.fromtimestamp(unix_time)
        now = date_time
        rounded = now - (now - datetime.min) % timedelta(minutes=5)
        return rounded.timestamp()
    """
    Rounds the given unix epoch of 5 minutes.
    """ 
    def get_timezone_based_timestamp(self,timezone=None):
        timezone = "Europe/Rome" if timezone is None else timezone
        tz= pytz.timezone(timezone)  #"Europe/Rome"
        timestamp = datetime.now(tz)
        return timestamp
    
    """
    Build the message composed by the resource path, the :*:*: separator and the rounded unix time.
    The message will be used to verify the given signature.
    """ 
    def encode_for_header(self,resource,time):
        w3=Web3(Web3.WebsocketProvider(WEBPROVIDER))
        msg_to_hash=resource+":*:*"+time
        msghash = w3.eth.account.sign_message(encode_defunct(text=msg_to_hash), private_key=private_key)
        print("From Header : ", resource,msghash)
        return msghash
    
    def encode_unsigned(self,resource,time):
        msghash = encode_defunct(text= resource+":*:*"+time )
        print("Verify : ", msghash)
        return msghash
    
    """
    Verifies if the signature extracted from the HTTP request has been signed by the claimed identity's credentrials.
    Makes use of the unsigned authentication message build according to the requested resource and the acutal rounded unix epoch.
    """    
    def authenticate_signature(self,sign,msg_hash,claim):
        print(claim,self.w3.eth.account.recover_message(msg_hash, signature=sign))
        return claim==self.w3.eth.account.recover_message(msg_hash, signature=sign)
    """
    Wrapper function to authenticate the signature extracted from a HTTP request.
    """     
    def authenticate(self,resource,signature,claim):

        ip_location_details = DTauthenticator.get_location(DTauthenticator)
        if (ip_location_details is None):
            return False
        current_time=self.get_timezone_based_timestamp(ip_location_details['timezone'])
        rounded=self.rounded_to_the_last_5th_minute_epoch(int(current_time.timestamp()))
        msg_hash=self.encode_unsigned(resource,str(rounded))
        signature = HexBytes(signature)
        print("is authenticated: "+str(self.authenticate_signature(signature,msg_hash,claim)))
        return self.authenticate_signature(signature,msg_hash,claim)

    def authenticate_country_with_ip(self,authorized_country):
        ip_location_details = DTauthenticator.get_location(DTauthenticator)
        if (ip_location_details is None):
            return ip_location_details
        print(authorized_country['name'], ip_location_details['country'] )
        return authorized_country['country_code'].lower() == ip_location_details['country_code'].lower()

    def validate_private_public_keys(public_key,private_key):
        try:
            w3=Web3(Web3.WebsocketProvider(WEBPROVIDER))
            pub_key =w3.eth.account.from_key(private_key)
            pub_key = pub_key.address
            return pub_key == public_key
        except Exception as e:
            print("An error occurred "+repr(e))
            return False