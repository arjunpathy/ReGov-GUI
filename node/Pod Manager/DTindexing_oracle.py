from web3 import Web3,WebsocketProvider
from eth_account import Account
from DTaddress_generator import DTaccount_generator
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from DTload_abi import load_abi_from_json
from DTaddresses import *
import os
DIR_PATH = os.path.abspath(os.path.dirname(__file__))

"""
Class that implements the communication mechanisms with the DTindexing smart contract.
"""
class DTindexing_oracle:

    """
    Class initializer.
    The function takes as input the DTindexing address and the private key of the pod.
    """
    def __init__(self, *args, **kw):
        self.indexing_address=args[0]
        self.contract_abi= load_abi_from_json(os.path.abspath(os.path.join(DIR_PATH,"../../build/contracts/DTindexing.json")))
        self.private_key=args[1]
        self.account= Account.from_key(self.private_key)
        
        print("contract address : "+self.indexing_address)
        
        self.provider=Web3(Web3.WebsocketProvider(WEBPROVIDER))
        self.contract_instance = self.provider.eth.contract(address=self.indexing_address, abi=self.contract_abi)
    """
    Marks a given pod's resource as non-active.
    Generates a transaction and invokes the deactivateResource() method of the DTindexing smart contract.
    """       
    def deactivate_resource(self,resource_id):

        transaction = {'from': self.account.address,'gasPrice': Web3.to_wei(21, 'gwei'),'nonce': self.provider.eth.get_transaction_count(self.account.address)}

        tx=self.contract_instance.functions.deactivateResource(resource_id).transact(transaction)
        receipt=self.provider.eth.waitForTransactionReceipt(tx)
        if receipt:
            return True
        else:
            return "False"
    """
    Initialize a new resource and adds it to the pod.
    Generates a transaction and invokes the registerResource() method of the DTindexing smart contract.
    Waits the emission of a NewResource event to retrieve the resource id.
    """     
    def add_resource(self,podId,reference,subscription):
        

        transaction = {'from': self.account.address,'gasPrice': Web3.to_wei(21, 'gwei'),'nonce': self.provider.eth.get_transaction_count(self.account.address)}
        
        tx_hash=self.contract_instance.functions.registerResource(podId, reference, subscription).transact(transaction)
        retVal = self.provider.eth.wait_for_transaction_receipt(tx_hash)
        processed_receipt=self.contract_instance.events.NewResource().processReceipt(retVal)
        print(processed_receipt)

        
        id=processed_receipt[0]['args']['idResource']
        return id
    """
    Reads the resources of a given pod.
    Calls the getPodResources() method of the DTindexing smart contract.
    """         
    def get_resource_information(self,pod_id,sub_id=0):
        
        resources =  self.contract_instance.functions.getPodResources(pod_id,sub_id).call({'from': self.account.address})
        return resources
    
    def get_resource_by_id(self,res_id):
        try:
            resource =  self.contract_instance.functions.getResource(res_id).call({'from': self.account.address})
            return resource
        except Exception as e:
            print(f"An error occurred: {e}")

    """
    Registers a new pod in the DecentralTrading market.
    Generates a transaction and invokes the registerPod() method of the DTindexing smart contract.
    Waits the emission of a NewPod event to retrieve the identifier of the new pod.
    """ 
    def register_Pod(self,pod_reference,pod_type,public_key_owner,private_key_owner):

        transaction = {'from':public_key_owner,'gas':5000000,'gasPrice': Web3.to_wei(50, 'gwei'),'nonce': self.provider.eth.get_transaction_count(public_key_owner)}
        
        tx_hash=self.contract_instance.functions.registerPod(pod_reference,pod_type,(public_key_owner)).transact(transaction)
        
    
        retVal = self.provider.eth.wait_for_transaction_receipt(tx_hash)  
        
        processed_receipt= self.contract_instance.events.NewPod().processReceipt(retVal)        
        id = processed_receipt[0]['args']['idPod'] 
        obligation_address= processed_receipt[0]['args']['obligationAddress']
        return id,public_key_owner,private_key_owner,obligation_address
