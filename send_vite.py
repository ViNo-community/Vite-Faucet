#!/usr/bin/env python
# coding: utf-8
#

from accountBlock import AccountBlock, BlockType
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
token_id = os.getenv('token_id')

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
    return json_rpc(rpc_url, ab)


def get_account_info(address):
    ab = {
        "jsonrpc": "2.0",
        "id": 17,
        "method": "ledger_getAccountInfoByAddress",
        "params": [
            address
        ]
    }
    # Send request
    return json_rpc(rpc_url, ab)

def get_account_balance(address):

    response = get_account_info(address)

    if "error" in response:
        raise Exception(f"Error grabbing acount info: {response}")

    result = response['result']  
    balanceInfo = result['balanceInfoMap']   
    viteInfo = balanceInfo['tti_5649544520544f4b454e6e40']
    balance = float(viteInfo['balance'])
    return Common.rawToVite(balance)

# Return PoW difficulty for sending transaction
def get_pow_difficulty(address,toAddress,prevHash,data=""):
    
    ab = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ledger_getPoWDifficulty",
        "params": [{
            "address": address,
            "previousHash": prevHash,
            "blockType": 2,
            "toAddress": toAddress,
            "data":data
        }]
    }
    # Send request
    return json_rpc(rpc_url, ab)


# _send_vite function with private key
def _send_vite(from_address, to_address, amount, data, tokenId, key):

    balance = get_account_balance(from_address)
    print(f"Account: {from_address} Balance: {balance}")
    
    # Make sure that we have enough funds to cover transaction
    if(amount >= balance):
        raise Exception(f"Insufficient funds. Balance: {balance} Amount requested: {amount}")

    response = get_previous_account_block(to_address)

    if "error" in response:
        raise Exception(f"Error grabbing previous account block: {response}")        

    # Grab height and hash info for previous account block
   
    result = response['result']

    if(result is None):
         print(f"Result is NONE")
         height = 0
         prevHash = 0
    else:
        height = result['height']
        prevHash = result['prevHash']
        print(f"Height: {height} Previous Hash: {prevHash}")

    # Get PoW difficult
    #response = get_pow_difficulty(from_address, to_address, prevHash)

    # If error return error result
    #if "error" in result:
    #    return result['error']

    #result = response['result']
    #requiredQuota = result['requiredQuota']
    #difficulty = result['difficulty']
    #qc = result['qc']

    #print(f"Required: {requiredQuota} Difficult: {difficulty} qc = {qc}")

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
            "privateKey": key,
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

