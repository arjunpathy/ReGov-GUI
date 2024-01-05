import os
from web3 import Web3
from eth_account import Account
import secrets
import web3
from DTload_abi import load_abi_from_json 
from DTaddresses import WEBPROVIDER
DIR_PATH = os.path.abspath(os.path.dirname(__file__))

"""
Class that implements the communication mechanisms with the DTsubscription smart contract.
"""
class DTsubscription_oracle:
    """
    Initalization of the class. 
    The function takes as input the address of the DTsubscription smart contract and its ABI.
    """
    def __init__(self, *args, **kw):
        self.subscription_address=args[0]
        self.contract_abi=load_abi_from_json(os.path.abspath(os.path.join(DIR_PATH,"../../build/contracts/DTsubscription.json")))
        self.private_key=args[1]
        self.account= Account.from_key(self.private_key)
        self.provider=Web3(Web3.WebsocketProvider(WEBPROVIDER))
        self.contract_instance = self.provider.eth.contract(address=self.subscription_address, abi=self.contract_abi)

    """
    Verifies that the subscription id is valied and is related to the claimed identity.
    """       
    def pull_subscription_verification(self,id_subscription,claim):
        result=self.contract_instance.functions.verify_subscription(id_subscription,Web3.toChecksumAddress(claim)).call({'from': self.account.address})
        print("is subscription verified: ",result)
        return result



