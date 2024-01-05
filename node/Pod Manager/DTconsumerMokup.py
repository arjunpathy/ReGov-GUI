import os 
from web3 import Web3
import asyncio
from DTaddresses import *
from DTobligation_oracle import DTobligation_oracle
from DTload_abi import load_abi_from_json
from DTutilities import *
from DTaddress_generator import *
from eth_account import Account

keys = DTaccount_generator.generate_account()
private_key = keys[1] 
STOP_MONITORING = False
DIR_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_POD_LOCATION = DEFAULT_POD_LOCATION + '/' if DEFAULT_POD_LOCATION[-1] != '/' else DEFAULT_POD_LOCATION

monitoring_contract_abi= load_abi_from_json(os.path.abspath(os.path.join(DIR_PATH,"../../build/contracts/DTmonitoringOracle.json")))
obligation_contract_abi= load_abi_from_json(os.path.abspath(os.path.join(DIR_PATH,"../../build/contracts/DTobligations.json")))

try:
    provider=Web3(Web3.WebsocketProvider(WEBPROVIDER))
    monitoring_contract_instance = provider.eth.contract(address=DTMONITORING, abi=monitoring_contract_abi)
except Exception as e:
    print(f"An error occurred: {e}")
account = Account.from_key(private_key)

class DTmonitoringMockup:

    def listen_monitoring(self):
            try:
                events = monitoring_contract_instance.events.NewMonitoring.createFilter(fromBlock='latest')
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        asyncio.gather(self.log_loop(events, 2)))
                finally:
                    loop.close()
            except Exception as e:
                print(f"An error occurred: {e}")

    async def log_loop(self,event_filter, poll_interval):
            while not STOP_MONITORING:
                for NewMonitoring in event_filter.get_new_entries():
                    self.handle_event(NewMonitoring)
                await asyncio.sleep(poll_interval)


    def handle_event(self,event):
            usage_log = self.usage_log_from_consumer()
            consumer_address = event["args"]['obligationsContract']
            monitoring_id = event["args"]['idMonitoring']
            resource_id = event["args"]['idResource']

            function_call = monitoring_contract_instance.functions._callback(consumer_address,monitoring_id,resource_id , usage_log)
            try:
                obligation_contract_instance = provider.eth.contract(address=consumer_address, abi=obligation_contract_abi)
                tx_hash = function_call.transact(
                    {'from': account.address, 'gasPrice': Web3.toWei(21, 'gwei'),
                     'nonce': provider.eth.getTransactionCount(account.address)})
                ret_val = provider.eth.wait_for_transaction_receipt(tx_hash)
                processed_receipt = obligation_contract_instance.events.NewMonitoringResponse().processReceipt(ret_val)
                log_entry = self.get_log_entry(event["args"], processed_receipt[0]['args'])
                # print(log_entry)

            except Exception as e:
                print(f"An error occurred: {e}")


    def get_log_entry(self,newMonitoring,monitoringResponse):
            current_datetime = datetime.now()
            timestamp = int(current_datetime.timestamp())
            log_entry = {
                "timestamp": timestamp,
                "resource_monitored": newMonitoring['idResource'],
                "monitoring_id" : newMonitoring['idMonitoring'],
                "request_status": "received", ####
                "outcome": 'successful', ####
                "consumer_address": monitoringResponse['consumer'],
                "log_file": monitoringResponse['response'].decode('utf-8'),
            }
            file_path = DEFAULT_POD_LOCATION+"logs.json"
            file_exist= os.path.exists(file_path)
            if file_exist:
                 data = readFileData(file_path)
                 data = data['logs']
                 data.append(log_entry)
                 updateFileData({"logs": data},file_path)
            else :
                with open(file_path, "w") as outfile:
                    json.dump({"logs": [log_entry]},outfile)

            return log_entry


    def usage_log_from_consumer(self):
        file_exist=os.path.exists(os.path.abspath(os.path.join(DIR_PATH,"../sample_log.txt")))
        if file_exist:
            fp = open(os.path.abspath(os.path.join(DIR_PATH,"../sample_log.txt")),'rb') # rb
            data = fp.read()
            fp.close()
            return data
        return None