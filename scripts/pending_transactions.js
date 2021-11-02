#!/usr/bin/env node

// Usage: ./send_vite.js [vite_address] [vite_amount]
const vite = require("@vite/vitejs")
const HTTP_RPC = require("@vite/vitejs-http").default
const WS_RPC = require("@vite/vitejs-ws").default
const config = require("./config.json")
const BigNumber = require("bignumber.js").default

const url = new URL(config.VITE_NODE)
let blocksSent = 0

// Set up Vite API (either WS or HTTP)
const provider = /^wss?:$/.test(url.protocol) ? 
    new WS_RPC(config.VITE_NODE, 6e5, {
        protocol: "",
        headers: "",
        clientConfig: "",
        retryTimes: Infinity,
        retryInterval: 10000
    }) : /^https?:$/.test(url.protocol) ? 
    new HTTP_RPC(config.VITE_NODE) :
    new Error("Invalid node url: "+config.VITE_NODE)
if(provider instanceof Error)throw provider

const ViteAPI = new vite.ViteAPI(provider, async () => {
    let address
    switch(config.VITE_LOGIN.type){
        case "mnemonic": {
            config.VITE_LOGIN.type = "seed"
            config.VITE_LOGIN.credentials = vite.wallet.getSeedFromMnemonics(config.VITE_LOGIN.credentials).seedHex
        }
        case "seed": {
            config.VITE_LOGIN.type = "private_key"
            config.VITE_LOGIN.credentials = vite.wallet.deriveKeyPairByIndex(config.VITE_LOGIN.credentials, config.VITE_LOGIN.index).privateKey
            config.VITE_LOGIN.index = 0
        }
        case "private_key": {
            if(config.VITE_LOGIN.index !== 0)throw new Error("Invalid index with private key: "+config.VITE_LOGIN.index)
            address = vite.wallet.createAddressByPrivateKey(config.VITE_LOGIN.credentials)
            break
        }
        default: {
            throw new Error("Invalid configuration for VITE_LOGIN")
        }
    }
    await new Promise((r) => setImmediate(r))

    try{
        // Receive pending transactions for this address
        await receivePendingTx(address)
        console.log(blocksSent)
        process.exit(0)
    } catch(err) {
        console.error(err)
        process.exit(1)
    }
})


async function receivePendingTx(address) {
    try {
        //console.log("Looking for pending transactions for" + address.address)
        // Grab RECEIVE_PER_ROUND blocks of pending transactions for address
        const RECEIVE_PER_ROUND = 10;
        let blocks = await ViteAPI.request('ledger_getUnreceivedBlocksByAddress', address.address, 0, RECEIVE_PER_ROUND);
        // Loop thru blocks in unreceived blocks by address
        // And receive them by hash
        //console.log(blocks.length + " transactions found for " + address.address)
        for (let i =0; i < blocks.length; i++) {
            let block = blocks[i];
            // Receive transaction with that hash
            await receiveTx(address, block.hash);
        }
        // Recursively call until no more pending transactions
        if (blocks.length >= RECEIVE_PER_ROUND) {
            await receivePendingTx(ViteAPI, address);
        }
    } catch(e) {
        // Log error and exit with status 1
        console.error("Error in receivePendingTx: ", e)
        console.trace()
        process.exit(1)
    }
    
}

async function receiveTx(address, sendBlockHash ) {
    try {
        // Create a receive account block with the sendblockhash
        //console.log("Creating account block with sendblockhash of " + sendBlockHash )
        const accountBlock = vite.accountBlock.createAccountBlock("receive", {
            address: address.address,
            sendBlockHash: sendBlockHash
        })
        // Set vite client and private key
        accountBlock.setProvider(ViteAPI).setPrivateKey(address.privateKey);
        // Find out how much quota is needed
        const [quota,difficulty] = await Promise.all([
            ViteAPI.request("contract_getQuotaByAccount", address.address),
            accountBlock.autoSetPreviousAccountBlock()
            .then(() => ViteAPI.request("ledger_getPoWDifficulty", {
                address: accountBlock.address,
                previousHash: accountBlock.previousHash,
                blockType: accountBlock.blockType,
                toAddress: accountBlock.toAddress,
                data: accountBlock.data
            }))
        ])
        // Set up PoW if needed
        const availableQuota = new BigNumber(quota.currentQuota)
        if(availableQuota.isLessThan(difficulty.requiredQuota)){
            await accountBlock.PoW(difficulty.difficulty)
        }
        // Sign and send it
        let result = await accountBlock.sign().send();
        //console.log(JSON.stringify(result, null, 4));
        blocksSent++;
        return result;
    } catch(e) {
        // Log error and exit with status 1
        console.error("Error in receivePendingTx: ", e)
        console.trace()
        process.exit(1)
    }
}