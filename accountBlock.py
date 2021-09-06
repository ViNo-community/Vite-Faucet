import json
from requests import sessions
from common import Common
import os
from enum import Enum

rpc_url = os.getenv('rpc_url')
rpc_timeout = float(os.getenv('rpc_timeout'))

ADDR_PREFIX = 'vite_'
ADDR_SIZE = 20
ADDR_CHECK_SUM_SIZE = 5
ADDR_LEN = len(ADDR_PREFIX) + ADDR_SIZE * 2 + ADDR_CHECK_SUM_SIZE * 2

class BlockType(Enum):
    CreateContractRequest = 1
    TransferRequest = 2
    ReIssueRequest = 3
    Response = 4
    ResponseFail = 5
    RefundByContractRequest = 6
    GenesisResponse = 7

class AddressType(Enum): 
    Illegal = 0,
    User = 1,
    Contract = 2

class AccountBlock:

    blockType = BlockType.TransferRequest
    height = 0
    hash = ""
    previousHash = ""
    address = ""
    publicKey = ""
    toAddress = ""
    tokenId = ""
    amount = 0
    data = ""
    privateKey = ""
    publicKey = ""
    signature = ""

    def __init__(self):
        return

    def getBlockType(self):
        return self.blockType
    def setBlockType(self,blockType):
        self.blockType = blockType

    def getHeight(self):
        return self.height
    def setHeight(self,height):
        self.height = height

    def getPreviousHash(self):
        return self.previousHash
    def setPreviousHash(self,previousHash):
        self.previousHash = previousHash

    def getToAddress(self):
        return self.toAddress
    def setToAddress(self, toAddress):
        self.toAddress = toAddress

    def getAmount(self):
        return self.amount
    def setAmount(self,amount):
        self.amount = amount

    def getTokenID(self):
        return self.tokenId
    def setTokenID(self,tokenID):
        self.tokenID = tokenID


    def getData(self):
        return self.data
    def setData(self,data):
        self.data = data

    def toJson(self):
        json = {
                "blockType": 2,     # Transfer Request
                "height": self.height,
                "hash": self.hash,
                "previousHash": self.previousHash,
                "address": self.from_address,
                "publicKey": self.publicKey,
                "toAddress": self.toAddress,
                "tokenId": self.tokenID,
                "amount": self.amount,
                "fee": "0",
                "data": "",
                "signature": "F5VzYwsNSr6ex2sl9hDaX67kP9g4TewMWcw7Tp57VkE1LQZO0i1toYEsXJ3MgcZdsvP67EymXXn1wpwhxnS3CQ=="
            }
        return json
    
    # Converts account block to a hash
    # For send transactions:
    # hash = HashFunction(BlockType + PrevHash  + Height + AccountAddress + ToAddress + Amount + TokenId + Data + Fee + LogHash + Nonce + sendBlock + hashList）
    def toHash(self):
        
        hash = ""
        hash += self.blockType.hex()         # BlockType
        hash += self.previousHash            # Already hashed
        hash += self.height.hex()   

        return hash

    def json_rpc(self,rpc_url, payload):
        Common.logger.debug(f"Payload: {json.dumps(payload)}")
        response = sessions.post(rpc_url, json=payload, timeout=rpc_timeout).json()
        Common.logger.debug(f"Response: {json.dumps(response)}")
        return response

    def get_previous_account_block(self,address):
        ab = {
            "jsonrpc": "2.0",
            "id": 17,
            "method": "ledger_getLatestAccountBlock",
            "params": [
                address
            ]
        }
        # Send request
        return self.json_rpc(rpc_url, ab)