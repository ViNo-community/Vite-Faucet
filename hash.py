from requests.models import InvalidURL
from accountBlock import AccountBlock, AddressType
from common import Common
from pyblake2 import blake2b

Default_Hash = '0000000000000000000000000000000000000000000000000000000000000000'; # A total of 64 0

def getAccountBlockHash(accountBlock): 

    source = ""
    source += getBlockTypeHex(accountBlock.blockType)
    source += getPreviousHashHex(accountBlock.previousHash)
    source += getHeightHex(accountBlock.height)
    source += getAddressHex(accountBlock.address)

    #source += getAddressHex(accountBlock.toAddress)
   # source += getAmountHex(accountBlock.amount)
    #source += getTokenIdHex(accountBlock.tokenId)
 

    #source += getDataHex(accountBlock.data)
    #source += getFeeHex(accountBlock.fee)

    #source += getNonceHex(accountBlock.nonce)


 #   const sourceHex = Buffer.from(source, 'hex');
#    const hashBuffer = blake.blake2b(sourceHex, null, 32);
    return source

def getBlockTypeHex(blockType):
    return str(blockType).encode("hex")

# If previousHash is defined, return it, otherwise return Default_Hash
def getPreviousHashHex(previousHash): 
    if(previousHash is None):
        return Default_Hash
    else:
        return previousHash

# Return height left-padded to 8 digits then hashed, or ""
def getHeightHex(height):
    if(height is None):
        return ''
    else:
        return Common.leftPadZeros(height, 8).encode('hex')

def getAddressHex(address):
    if(address is None):
        return ''
    else:
        return getOriginalAddress(address)

# Get the original address from the literal address and address type
def getOriginalAddress(literalAddress, addressType): 
    # Original address is bytes 6 to 45
    # Ex:[vite_][48171fc674cffc8cc4e0b2e7544ba468d31cbdce][1fc35cba02]
    #     PRE..ORIGINAL_ADDRESS_______________________CHKSUM____
    originalAddress = literalAddress[AccountBlock.ADDR_PREFIX.length, AccountBlock.ADDR_PREFIX.length + AccountBlock.ADDR_SIZE * 2]
    # Append address type ID (00 for user account, 01 for contract)
    if (addressType == AccountBlock.AddressType.User):
        return f"{originalAddress}00"
    else:
        return f"{originalAddress}01"

# Check if address is valid. Not null, correct length, starts with "vite_"
def isValidAddress(address):
    # Address is null
    if(address is None):
        return False
    # Invalid length
    if(len(address) != AccountBlock.ADDR_LEN):
        return False
    try:
        # "vite_" not at beginning of address
        if(address.index(AccountBlock.ADDR_PREFIX) != 0):
            return False
    except ValueError:
        # "vite_" not found
        return False
    if(getAccountType(address) != AccountBlock.AddressType.Illegal):
        return True

# Returns the type of account the given address is. 
# Either Contract, User, or Illegal.
def getAccountType(address): 
    # Grab the checksum portion of the address
    currentChecksum = address.slice(AccountBlock.ADDR_PREFIX.length + AccountBlock.ADDR_SIZE * 2)
    # Grab the account body portion
    addressBody = address.slice(AccountBlock.ADDR_PREFIX.length, AccountBlock.ADDR_PREFIX.length + AccountBlock.ADDR_SIZE * 2)
    addressBodyHash = addressBody.encode('hex')

    contractCheckSum = getAddressCheckSum(addressBodyHash, True)
    if (contractCheckSum == currentChecksum):
        return AccountBlock.AddressType.Contract

    checkSum = getAddressCheckSum(addressBodyHash)
    if (currentChecksum == checkSum):
        return AccountBlock.AddressType.User

    return AccountBlock.AddressType.Illegal

# Return the address check sum
# If User then return hash(blake2b(original_adress))
# If Contract then return flipped hash(blake2(original_address))
def getAddressCheckSum(address, isContract = False): 
    # Grab first ADDR_SIZE bytes of address
    addressBody = address.slice(0, AccountBlock.ADDR_SIZE)
    # Calculate the blake2b 
    checkSum = blake2b(addressBody, AccountBlock.ADDR_CHECK_SUM_SIZE)

    # If User account returns hash of blake2b
    if (not isContract):
        return checkSum.toString('hex')

    # Otherwise returns hash of flipped blake2b
    newCheckSum = []
    i = 0
    for byte in checkSum:
        newCheckSum[i] = byte ^ 0xFF
        i = i + 1
    return newCheckSum.encode("hex")

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
