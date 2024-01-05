import os 
from web3 import Web3
from eth_account import Account
import asyncio
from DTaddresses import WEBPROVIDER
from DTaddress_generator import DTaccount_generator
from DTload_abi import load_abi_from_json

keys = DTaccount_generator.generate_account()
public_key = keys[0]
DIR_PATH = os.path.abspath(os.path.dirname(__file__))

"""
Class that implements the communication mechanisms with the DTobligations smart contract.
"""
class DTobligation_oracle:



    """
    Class initializer.
    The function takes as input the address of the DTobligations smart contract and its ABI.
    """
    def __init__(self, *args, **kw):
        self.indexing_address=args[0]
        self.contract_abi= load_abi_from_json(os.path.abspath(os.path.join(DIR_PATH,"../../build/contracts/DTobligations.json")))
        self.private_key=args[1]
        self.account= Account.from_key(self.private_key)
        self.provider=Web3(Web3.WebsocketProvider(WEBPROVIDER))
        self.contract_instance = self.provider.eth.contract(address=self.indexing_address, abi=self.contract_abi)
        self.STOP_MONITORING=False
    """
    Sets an access counter obligation valid for the whole pod.
    Invokes the addDefaultAccessCounterObligation() method of the DTobligation smart contract.
    """        
    def set_default_access_counter_obligation(self,access_counter):
        tx=self.contract_instance.functions.addDefaultAccessCounterObligation(access_counter).buildTransaction({'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
        
    """
    Sets a temporal obligation valid for the whole pod.
    Invokes the addDefaultTemporalObligation() method of the DTobligation smart contract.
    """
    def set_default_temporal_obligation(self,temporalObligation):
        tx=self.contract_instance.functions.addDefaultTemporalObligation(temporalObligation).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Remove an access counter obligation valid for the whole pod.
    Invokes the removeDefaultAccessCounterObligation() method of the DTobligation smart contract.
    """
    def deactivate_default_access_counter_obligation(self):
        tx=self.contract_instance.functions.removeDefaultAccessCounterObligation().buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Remove a temporal obligation valid for the whole pod.
    Invokes the removeDefaultTemporalObligation() method of the DTobligation smart contract.
    """
    def deactivate_default_temporal_obligation(self):
        tx=self.contract_instance.functions.removeDefaultTemporalObligation().buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Sets an access counter obligation associated with a specific resource.
    Invokes the addAccessCounterObligation() method of the DTobligation smart contract.
    """        
    def set_access_counter_obligation(self,id,access_counter):
        tx=self.contract_instance.functions.addAccessCounterObligation(id,access_counter).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Sets an access counter obligation associated with a specific resource.
    Invokes the addTemporalObligation() method of the DTobligation smart contract.
    """ 
    def set_temporal_obligation(self,id,temporalObligation):
        tx=self.contract_instance.functions.addTemporalObligation(id,temporalObligation).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Deactivate an access counter obligation associated with a specific resource.
    Invokes the removeAccessCounterObligation() method of the DTobligation smart contract.
    """ 
    def deactivate_access_counter_obligation(self,id):
        tx=self.contract_instance.functions.removeAccessCounterObligation(id).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Deactivate a temporal obligation associated with a specific resource.
    Invokes the removeTemporalObligation() method of the DTobligation smart contract.
    """ 
    def deactivate_temporal_obligation(self,id):
        tx=self.contract_instance.functions.removeTemporalObligation(id).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Sets a country obligation for the whole pod.
    Invokes the addDefaultCountryObligation() method of the DTobligation smart contract.
    """ 
    def set_default_country_obligation(self,country):
        tx=self.contract_instance.functions.addDefaultCountryObligation(country).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))        
    """
    Sets a country obligation associated with a specific resource.
    Invokes the addCountryObligation() method of the DTobligation smart contract.
    """ 
    def set_country_obligation(self,id,country):
        tx=self.contract_instance.functions.addCountryObligation(id,country).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))    
    """
    Sets a domain obligation associated with a specific resource.
    Invokes the addDomainObligation() method of the DTobligation smart contract.
    """     
    def set_domain_obligation(self,id,domain):
        tx=self.contract_instance.functions.addDomainObligation(id,domain).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Sets a domain obligation for the whole pod.
    Invokes the addDefaultDomainObligation() method of the DTobligation smart contract.
    """ 
    def set_default_domain_obligation(self,domain):
        tx=self.contract_instance.functions.adDefaultDomainObligation(domain).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Deactivate a domain obligation associated with a specific resource.
    Invokes the removeDomainObligation() method of the DTobligation smart contract.
    """     
    def deactivate_domain_obligation(self,id):
        tx=self.contract_instance.functions.removeDomainObligation(id).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Deactivate a domain obligation for the whole pod.
    Invokes the removeDefaultDomainObligation() method of the DTobligation smart contract.
    """     
    def deactivate_default_domain_obligation(self):
        tx=self.contract_instance.functions.removeDefaultDomainObligation().buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Deactivate a country obligation for the whole pod.
    Invokes the removeDefaultCountryObligation() method of the DTobligation smart contract.
    """
    def deactivate_default_country_obligation(self):
        tx=self.contract_instance.functions.removeDefaultCountryObligation().buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))
    """
    Deactivate a country obligation associated with a specific resource.
    Invokes the removeCountryObligation() method of the DTobligation smart contract.
    """
    def deactivate_country_obligation(self,id):
        tx=self.contract_instance.functions.removeCountryObligation(id).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
        signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
        print(self.provider.eth.waitForTransactionReceipt(tx))

    def listen_monitoring_response(self):
        try:
            events = self.contract_instance.events.NewMonitoringResponse.createFilter(fromBlock='latest')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(asyncio.gather(self.log_loop(events, 4)))
            finally:
                loop.close()
        except Exception as e:
            print(f"An error occurred: {e}")
   
    def stop_monitoring(self):
        self.STOP_MONITORING=True
    
    async def log_loop(self,event_filter, poll_interval):
        print("Listening for monitoring response from contract: {0}".format(self.indexing_address))
        try:
            while not self.STOP_MONITORING:
                for NewMonitoringResponse in event_filter.get_new_entries():
                    self.handle_event(NewMonitoringResponse)
                await asyncio.sleep(poll_interval)
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def handle_event(self,event):
        print("Response Receipt - Id Monitoring: {0}, Consumer: {1}, Response: {2}".format(event.args['idMonitoring'],event.args['consumer'],event.args['response']))

    def start_monitoring_routine(self,id_resource):
        try :
            tx=self.contract_instance.functions.monitor_compliance(id_resource).buildTransaction({'from': self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': self.provider.eth.getTransactionCount(self.account.address)})
            signed_txn = self.provider.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx=Web3.toHex(self.provider.eth.sendRawTransaction(signed_txn.rawTransaction))
            # print(self.provider.eth.waitForTransactionReceipt(tx))
        except Exception as e:
            print(f"An error occurred: {e}")

    def callback(self,contract_instance,provider, consumer_address, monitoring_id, resource_id, response):
        try :
            tx=contract_instance.functions._callback( consumer_address, monitoring_id, resource_id, response).buildTransaction({'from':self.account.address,'gasPrice': Web3.toWei(21, 'gwei'),'nonce': provider.eth.getTransactionCount(public_key)})
            # retVal = provider.eth.wait_for_transaction_receipt(tx)  
            # print(tx)
        except Exception as e:
            print(f"An error occurred: {e}")