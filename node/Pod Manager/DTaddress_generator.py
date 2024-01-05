from web3 import Web3
from eth_account import Account
import secrets
from DTaddresses import WEBPROVIDER

class DTaccount_generator():

    def __init__(self, *args, **kw):
        self.w3=Web3(Web3.WebsocketProvider(WEBPROVIDER))
    
    def generate_account():
        return ("0x07787075417DE12216663842B6aF0992C65058B1","35298825481e08cdeb4456079f1dcf4730af5e216c8075a701da7775a7c52d7b")
