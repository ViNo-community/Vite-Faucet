#!/usr/bin/env python
# coding: utf-8
#

import json
import time
import os
from dotenv.main import load_dotenv
import requests

session = requests.Session()
session.trust_env = False

# Loads the .env file that resides on the same level as the script.
load_dotenv()

rpc_url = os.getenv('rpc_url')

print (f"RPC_URL is {rpc_url}")

def json_rpc(rpc_url, payload):
    print(f"Sending json: {payload}")
    response = session.post(rpc_url, json=payload, timeout=2).json()
    print(json.dumps(payload), json.dumps(response))
    return response

# Grabs current ledger snapshot height
def height():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ledger_getSnapshotChainHeight",
        "params": []
    }
    result = json_rpc(rpc_url, payload)
    return result['result']

def confirmed_num(blockHash):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ledger_getAccountBlockByHash",
        "params": [blockHash]
    }
    result = json_rpc(rpc_url, payload)
    if result['result']['confirmations'] == None:
        return 0
    else:
        return int(result['result']['confirmations'])


# _send_vite function with private key
def _send_vite(from_address, to_address, amount, data, tokenId, priv):

    while int(height()) < 3:
        print("waiting snapshot height inc")
        time.sleep(2)

    payload = {
        "jsonrpc":
        "2.0",
        "id":
        1,
        "method":
        "tx_sendTxWithPrivateKey",
        "params": [{
            "selfAddr": from_address,
            "toAddr": to_address,
            "tokenTypeId": tokenId,
            "privateKey": priv,
            "amount": amount,
            "data": data,
            "blockType": 2
        }]
    }

    print(f"in _send_vite Payload: {payload}")
    result = json_rpc(rpc_url, payload)

    if "error" in result:
        return result['error']

    i = 0
    block = result['result']
    while int(confirmed_num(block['hash'])) < 3 and i < 3:
        i = i + 1
        print("waiting " + block['hash'] + ",confirm")
        time.sleep(2)
    return block['hash']

'''
def send_vite(to_address):
    print(f"send_vite to {to_address}")

    result = _send_vite(FAUCET_ADDRESS, to_address, TOKEN_AMOUNT, '', TOKEN_ID,
                          FAUCET_PRIVATE_KEY)
    if "error" in result:
        return result['error']

    i = 0
    block = result['result']
    while int(confirmedNum(block['hash'])) < 3 and i < 3:
        i = i + 1
        print("waiting " + block['hash'] + ",confirm")
        time.sleep(2)
    return block['hash']
'''