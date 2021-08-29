#!/usr/bin/env python
# coding: utf-8
#

import json
import os
from dotenv.main import load_dotenv
import requests
from common import Common

session = requests.Session()
session.trust_env = False

# Loads the .env file that resides on the same level as the script.
load_dotenv()

rpc_url = os.getenv('rpc_url')
rpc_timeout = float(os.getenv('rpc_timeout'))

print (f"RPC_URL is {rpc_url}")

def json_rpc(rpc_url, payload):
    Common.logger.debug(f"Payload: {json.dumps(payload)}")
    response = session.post(rpc_url, json=payload, timeout=rpc_timeout).json()
    Common.logger.debug(f"Response: {json.dumps(response)}")
    return response

def get_previous_account_block(address):
    ab = {
        "jsonrpc": "2.0",
        "id": 17,
        "method": "ledger_getLatestAccountBlock",
        "params": [
            address
        ]
    }
    # Send request
    response = json_rpc(rpc_url, ab)
    return response

# _send_vite function with private key
def _send_vite(from_address, to_address, amount, data, tokenId, priv):

    response = get_previous_account_block(to_address)

    #print(f"Height: {response['height']}")
    ##print(f"Hash: {response['hash']}")
    #print(f"Previous Hash: {response['previousHash']}")

    accountBlock = {
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
            "amount": str(int(round(Common.viteToRaw(amount)))),
            "data": data,
            "blockType": 2
        }]
    }

    # Send accountBlock
    result = json_rpc(rpc_url, accountBlock)
    # If error return error result
    if "error" in result:
        return result['error']
    return

    height = 2
    hash = ""
    prevHash = ""

    accountBlock = {
        "jsonrpc":"2.0",
        "id":1,
        "method":"ledger_sendRawTransaction",
        "params": [{
            "blockType": 2,     # Transfer Request
            "height": height,
            "hash": "67f4d528a5194c46d594221d3d992257a3004ccdee7c5d7b2748d77e06a80caf",
            "previousHash": "d517e8d4dc9c676876b72ad0cbb4c45890804aa438edd1f171ffc66276202a95",
            "address": from_address,
            "publicKey": "WHZinxslscE+WaIqrUjGu2scOvorgD4Q+DQOOcDBv4M=",
            "toAddress": to_address,
            "sendBlockHash": "0000000000000000000000000000000000000000000000000000000000000000",
            "tokenId": tokenId,
            "amount": str(int(round(Common.viteToRaw(amount)))),
            "fee": "0",
            "data": "jefc/QAAAAAAAAAAAAAAqyTvaLhOZCwN3KBr7sgcmssZd7sA",
            "signature": "F5VzYwsNSr6ex2sl9hDaX67kP9g4TewMWcw7Tp57VkE1LQZO0i1toYEsXJ3MgcZdsvP67EymXXn1wpwhxnS3CQ=="
        }]
    }

    # Send accountBlock
    result = json_rpc(rpc_url, accountBlock)
    # If error return error result
    if "error" in result:
        return result['error']
