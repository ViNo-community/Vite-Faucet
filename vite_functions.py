import json
import os
from dotenv.main import load_dotenv
import aiohttp
from common import Common
import subprocess

# Loads the .env file that resides on the same level as the script.
load_dotenv()

rpc_url = os.getenv('rpc_url')
rpc_timeout = float(os.getenv('rpc_timeout'))
token_id = os.getenv('token_id')

RETRY_AMOUNT = 3

# Post JSON payload to RPC_URL and return result
async def client_post(rpc_url, payload):
    try:
        Common.logger.debug(f"Payload: {json.dumps(payload)}")
        async with aiohttp.ClientSession() as session:
            # Make POST request
            resp = await session.post(rpc_url,json=payload,timeout=rpc_timeout)
            # Grab text
            text = await resp.text()
            Common.logger.debug(f"Response: {text}")
            # Return JSON loaded from text
            return json.loads(text)
    except Exception as e:
        Common.logger.error(f"Error in client_post: {e}", exc_info=True)  

# Get account information for specified address
async def get_account_info(address):
    try:
        # Make payload
        payload = {
            "jsonrpc": "2.0",
            "id": 17,
            "method": "ledger_getAccountInfoByAddress",
            "params": [ address ]
        }
        # Send request
        response = await client_post(rpc_url, payload)
        return response
    except Exception as e:
        Common.logger.error(f"Error in get_account_info: {e}", exc_info=True)  

# Get account balance in Vite for specified account
async def get_account_balance(address):
    try:
        # Try RETRY_AMOUNT times
        retries = 0
        response = None
        # Get account info for this address
        while(response is None and retries < RETRY_AMOUNT):
            response = await get_account_info(address)
            retries = retries + 1
        # Raise exception if response is None
        if(response is None):
            raise Exception("Null response for get_account_balance")
        if "error" in response:
            raise Exception(f"Error grabbing account balance: {response}")
        # Get balance for VITE from balanceInfoMap
        result = response['result']  
        balanceInfo = result['balanceInfoMap']   
        viteInfo = balanceInfo[token_id]
        balance = float(viteInfo['balance'])
        # Convert from raw to Vite
        return Common.rawToVite(balance)
    except Exception as e:
        Common.logger.error(f"Error in get_account_balance: {e}", exc_info=True)  

# Get quota balance in UT for specified address
async def get_account_quota(address):
    try:
        # Try RETRY_AMOUNT times
        retries = 0
        response = None
        # Make payload
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "contract_getQuotaByAccount",
            "params": [ address,]
        }
        # Send request. Try RETRY_AMOUNT times
        while(response is None and retries < RETRY_AMOUNT):
            response = await client_post(rpc_url, payload)
            retries = retries + 1
        # Raise exception if response is None
        if(response is None):
            raise Exception("Null response for get_account_balance")
        # If error response, raise exception
        if "error" in response:
            raise Exception(f"Error grabbing quota info: {response}")
        # Grab quota from JSON result
        result = response['result']  
        quota = int(result['currentQuota'])
        # Convert to UT and return
        return Common.quotaToUT(quota)
    except Exception as e:
        Common.logger.error(f"Error in get_account_quota: {e}", exc_info=True)  


# _send_vite function with private key
async def send_transaction(from_address, to_address, amount):
    try:
        retries = 0
        # Grab account balance for this account
        balance = await get_account_balance(from_address)
        # Make sure that we have enough funds to cover transaction
        if(amount >= balance):
            raise Exception(f"Insufficient funds. Balance: {balance} Amount requested: {amount}")
        # Call send_vite.js script
        command = ['node','scripts/send_vite.js', to_address, str(amount)]
        res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while(res.returncode == 1 and retries < RETRY_AMOUNT):
            res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) 
            retries = retries + 1
        return res
    # os.system(f"scripts/send_vite.js {to_address} {amount}")
    except Exception as e:
        Common.logger.error(f"Error in _send_vite: {e}", exc_info=True)  