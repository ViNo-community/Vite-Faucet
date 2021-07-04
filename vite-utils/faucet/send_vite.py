#!/usr/bin/env python
# coding: utf-8
#

import json
import time
import os
import requests

session = requests.Session()
session.trust_env = False

NODE_URL = 'http://127.0.0.1:48132'
if os.getenv('NODE_URL') != None:
    NODE_URL = os.getenv('NODE_URL')

from_address = os.getenv('FROM_ADDRESS')
from_priv = os.getenv('FROM_PRIV')
tokenId = os.getenv('TOKEN_ID')
amount = os.getenv('TOKEN_AMOUNT')

assert from_address is not None, 'environment variable[FROM_ADDRESS] must be set'
assert from_priv is not None, 'environment variable[FROM_PRIV] must be set'
assert tokenId is not None, 'environment variable[TOKEN_ID] must be set'
assert amount is not None, 'environment variable[TOKEN_AMOUNT] must be set'


def json_rpc(rpc_url, payload, thx=True):
    response = session.post(rpc_url, json=payload, timeout=2).json()
    print(json.dumps(payload), json.dumps(response))
    if thx:
        assert "error" not in response
        assert "Error" not in response
    return response


def height():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ledger_getSnapshotChainHeight",
        "params": []
    }
    result = json_rpc(NODE_URL, payload)
    return result['result']


def confirmedNum(blockHash):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ledger_getAccountBlockByHash",
        "params": [blockHash]
    }
    result = json_rpc(NODE_URL, payload)
    if result['result']['confirmations'] == None:
        return 0
    else:
        return int(result['result']['confirmations'])


def sendWithPriv(from_address, to_address, amount, data, tokenId, priv):
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
    result = json_rpc(NODE_URL, payload, False)
    return result


def sendVite(to_address):
    while int(height()) < 3:
        print("waiting snapshot height inc")
        time.sleep(2)
    result = sendWithPriv(from_address, to_address, amount, '', tokenId,
                          from_priv)
    if "error" in result:
        return result['error']
    i = 0
    block = result['result']
    while int(confirmedNum(block['hash'])) < 3 and i < 3:
        i = i + 1
        print("waiting " + block['hash'] + ",confirm")
        time.sleep(2)
    return block['hash']
