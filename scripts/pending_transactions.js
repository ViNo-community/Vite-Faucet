#!/usr/bin/env node

// Usage: ./send_vite.js [vite_address] [vite_amount]
const vite = require("@vite/vitejs")
const HTTP_RPC = require("@vite/vitejs-http").default
const WS_RPC = require("@vite/vitejs-ws").default
const config = require("./config.json")
const BigNumber = require("bignumber.js").default

// Set up Vite API client
const httpProvider = new HTTP_RPC(config.VITE_NODE);
var viteClient = new vite.ViteAPI(httpProvider, () => {
    console.log('Vite client successfully connected: ');
});

try{
    // Create wallet address from private key credentials in config.json
    let address =  vite.wallet.createAddressByPrivateKey(config.VITE_LOGIN.credentials)
    console.log("Using address " + address.address)
    // Receive pending transactions for this address
    receivePendingTx(address)
    // Exit with status 0 - success
    process.exit(0)
} catch(e) {
    // Log error and exit with status 1
    console.error("Error: " + e)
    console.trace()
    process.exit(1)
}

async function receivePendingTx(address) {
    try {
        console.log("In receivePendingTx for " + address.address)
        const accountBlock = await viteClient.request('ledger_getLatestAccountBlock', address);
        console.log(accountBlock)
        let blocks2 = await viteClient.request('ledger_getUnreceivedBlocksByAddress', address.address, 0, RECEIVE_PER_ROUND);

        const RECEIVE_PER_ROUND = 10;
        let blocks = await viteClient.request('ledger_getUnreceivedBlocksByAddress', address.address, 0, RECEIVE_PER_ROUND);
        console.log("After")
        // Loop thru blocks in unreceived blocks by address
        // And receive them by hash
        console.log(blocks.length + " transactions found for " + address.address)
        for (let i =0; i < blocks.length; i++) {
            let block = blocks[i];
            // Receive 
            await receiveTx(address, block.hash);
        }
        // Recursively call until no more pending transactions
        if (blocks.length >= RECEIVE_PER_ROUND) {
            await receivePendingTx(viteClient, address);
        }
    } catch(e) {
        // Log error and exit with status 1
        console.error("Error in receivePendingTx: " + e)
        console.trace()
        process.exit(1)
    }
    
}

async function receiveTx(address, { sendBlockHash }) {
    try {
        // Create a receive account block with the sendblockhash
        const accountBlock = vite.accountBlock.createAccountBlock("receive", {
            address: address.address,
            sendBlockHash: sendBlockHash
        })
        console.log("Receive transaction " + sendBlockHash)
        // Set vite client and private key
        accountBlock.setProvider(ViteAPI).setPrivateKey(address.privateKey)
        // Auto-fill previous hash and block height
        await accountBlock.autoSetPreviousAccountBlock();
        // Sign and send it
        let result = await accountBlock.sign().send();
        console.log(JSON.stringify(result, null, 4));
        return result;
    } catch(e) {
        // Log error and exit with status 1
        console.error("Error in receivePendingTx: " + e)
        console.trace()
        process.exit(1)
    }
}