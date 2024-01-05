import json

def load_abi_from_json(path):
    try:
        data = open(path,mode='r')
        data =json.load(data)['abi']
        return data
    except OSError:
        print("Abi not found. Deploy again!")
        return None