Default_Hash = '0000000000000000000000000000000000000000000000000000000000000000'; # A total of 64 0

def getAccountBlockHash(accountBlock): 

    source = ""
    source += getBlockTypeHex(accountBlock.blockType)
    source += accountBlock.previousHash
    #source += getHeightHex(accountBlock.height)
    #source += getAddressHex(accountBlock.address)

    #source += getAddressHex(accountBlock.toAddress)
   # source += getAmountHex(accountBlock.amount)
    #source += getTokenIdHex(accountBlock.tokenId)
 

    #source += getDataHex(accountBlock.data)
    #source += getFeeHex(accountBlock.fee)

    #source += getNonceHex(accountBlock.nonce)


 #   const sourceHex = Buffer.from(source, 'hex');
#    const hashBuffer = blake.blake2b(sourceHex, null, 32);
    return source

def getPreviousHashHex(previousHash): 
    return previousHash or Default_Hash


def getBlockTypeHex(blockType):
    return str(blockType).encode("hex")

'''
Reference: 
// Get AccountBlock.hash

// ****1.sendBlock
// hash = HashFunction(BlockType + PrevHash  + Height + AccountAddress + ToAddress + Amount + TokenId + Data + Fee + LogHash + Nonce + hashList）

// 2.receiveBlock
// hash = HashFunction(BlockType + PrevHash  + Height + AccountAddress + FromBlockHash + Data + Fee + LogHash + Nonce + sendBlock + hashList）

export function getAccountBlockHash(accountBlock: {
    blockType: BlockType;
    address: Address;
    hash?: Hex;
    height?: Uint64;
    previousHash?: Hex;
    fromAddress?: Address;
    toAddress?: Address;
    tokenId?: TokenId;
    amount?: BigInt;
    fee?: BigInt;
    data?: Base64;
    difficulty?: BigInt;
    nonce?: Base64;
}): Hex {
    let source = '';

    source += getBlockTypeHex(accountBlock.blockType);
    source += getPreviousHashHex(accountBlock.previousHash);

    source += Buffer.from([accountBlock.blockType]).toString('hex')
    source += accountBlock.previousHash
  
    source += getHeightHex(accountBlock.height);
    source += getAddressHex(accountBlock.address);

    source += getAddressHex(accountBlock.toAddress);
    source += getAmountHex(accountBlock.amount);
    source += getTokenIdHex(accountBlock.tokenId);


    source += getDataHex(accountBlock.data);
    source += getFeeHex(accountBlock.fee);
    source += getNonceHex(accountBlock.nonce);

    const sourceHex = Buffer.from(source, 'hex');
    const hashBuffer = blake.blake2b(sourceHex, null, 32);
    return Buffer.from(hashBuffer).toString('hex');
}


'''
