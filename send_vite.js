#!/usr/bin/env node
const vite = require("vitejs-notthomiz")
const HTTP_RPC = require("vitejs-notthomiz-http").default
const WS_RPC = require("vitejs-notthomiz-ws").default
const config = require("./config.json")
const BigNumber = require("bignumber.js").default

const [,,
    destination, amount
] = process.argv
if(!vite.wallet.isValidAddress(destination)){
    throw new Error("Invalid Address")
}
if(!/^\d+(\.\d+)?$/.test(amount)){
    throw new Error("Invalid Amount")
}

const url = new URL(config.VITE_NODE)
const provider = /^wss?:$/.test(url.protocol) ? 
    new WS_RPC(config.VITE_NODE, 6e5, {
        protocol: "",
        headers: "",
        clientConfig: "",
        retryTimes: Infinity,
        retryInterval: 10000
    }) : /^https?:$/.test(url.protocol) ? 
    new HTTP_RPC(config.VITE_NODE, 6e5) :
    new Error("Invalid node url: "+config.VITE_NODE)
if(provider instanceof Error)throw provider
console.log("Connecting to "+config.VITE_NODE)


const ViteAPI = new vite.ViteAPI(provider, async () => {
    console.log("Provider ready !")
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
    console.log("Using "+address.address+" as sender !")
    const actions = {
        send: async (tokenId, amount, destination) => {
            if(
                [tokenId, amount, destination].find(e => typeof e !== "string") ||
                !vite.utils.isValidTokenId(tokenId) ||
                !/^\d+$/.test(amount) ||
                !vite.wallet.isValidAddress(destination)
            )throw new Error("Invalid Arguments.")
            const balances = (await ViteAPI.request("ledger_getAccountInfoByAddress", address.address))?.balanceInfoMap || {}
            const balance = new BigNumber(balances[tokenId]?.balance || "0")
            if(balance.isLessThan(amount))throw new Error("Insufficient Balance")

            const accountBlock = vite.accountBlock.createAccountBlock("send", {
                toAddress: destination,
                address: address.address,
                tokenId: tokenId,
                amount: amount
            })
            accountBlock.setProvider(ViteAPI)
            .setPrivateKey(address.privateKey)
            const [
                quota,
                difficulty
            ] = await Promise.all([
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
            
            const availableQuota = new BigNumber(quota.currentQuota)
            if(availableQuota.isLessThan(difficulty.requiredQuota)){
                await accountBlock.PoW(difficulty.difficulty)
            }
            await accountBlock.sign()

            const hash = (await accountBlock.send()).hash

            return {
                hash: hash,
                from: address.address,
                to: destination,
                tokenid: tokenId,
                amount: amount
            }
        }
    }

    try{
        const result = await actions.send("tti_5649544520544f4b454e6e40", new BigNumber(amount).shiftedBy(18).toFixed().split(".")[0], destination)
        console.log(result)
        process.exit(0)
    }catch(err){
        console.error(err)
        process.exit(1)
    }
})