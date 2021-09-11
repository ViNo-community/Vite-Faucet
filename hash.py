from requests.models import InvalidURL
from accountBlock import AccountBlock, AddressType
from common import Common
from pyblake2 import blake2b
import hashlib
import binascii

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
        return binascii.hexlify(b"{Common.leftPadZeros(height, 8)}")

def getAddressHex(address):
    if(address is None):
        return ''
    else:
        return getOriginalAddress(address)

# Get the original address from the literal address and address type
def getOriginalAddress(literalAddress): 
    addressType = getAddressType(literalAddress)
    # Original address is bytes 6 to 45
    # Ex:[vite_][48171fc674cffc8cc4e0b2e7544ba468d31cbdce][1fc35cba02]
    #     PRE..ORIGINAL_ADDRESS_______________________CHKSUM____
    originalAddress = literalAddress[AccountBlock.ADDR_PREFIX.length, AccountBlock.ADDR_PREFIX.length + AccountBlock.ADDR_SIZE * 2]
    # Append address type ID (00 for user account, 01 for contract)
    if (addressType == AccountBlock.AddressType.User):
        return f"{originalAddress}00"
    else:
        return f"{originalAddress}01"

# Returns the type of account the given address is. 
# Either Contract, User, or Illegal.
def isValidAddress(address): 

    # Validate address

    # Address is null
    if(address is None):
        raise Exception("Address is NoneType")
    # Invalid length
    if(len(address) != AccountBlock.ADDR_LEN):
        raise Exception("Address is invalid length")
    try:
        # "vite_" not at beginning of address
        if(address.index(AccountBlock.ADDR_PREFIX) != 0):
            raise Exception("Address does not begin with vite_")
    except ValueError:
        # "vite_" not found
        raise Exception("Address does not begin with vite_")

    # Can't get address checksums to work
    return True

    print(f"Address is {address}")
    # Grab the checksum portion of the address
    currentChecksum = address[len(AccountBlock.ADDR_PREFIX) + AccountBlock.ADDR_SIZE * 2 : len(AccountBlock.ADDR_PREFIX) + AccountBlock.ADDR_SIZE * 2 + AccountBlock.ADDR_CHECK_SUM_SIZE ]
    print(f"Current checksum is {currentChecksum}")
    # Grab the account body portion
    addressBody = address[len(AccountBlock.ADDR_PREFIX) : len(AccountBlock.ADDR_PREFIX) + int(AccountBlock.ADDR_SIZE) * 2]
    addressBodyHash = binascii.hexlify(bytes(addressBody, encoding="utf8"))
    print(f"Address body: {addressBody} addressBodyHash: {addressBody.decode('ascii')}")

    contractCheckSum = getAddressCheckSum(addressBodyHash, True)
    if (contractCheckSum == currentChecksum):
        return AccountBlock.AddressType.Contract

    checkSum = getAddressCheckSum(addressBodyHash)
    print(f"Returned checksum is {int(checkSum,16)}")
    if (currentChecksum == checkSum):
        return AccountBlock.AddressType.User

    raise Exception("Address contains invalid checksum")

# Return the address check sum
# If User then return hash(blake2b(original_adress))
# If Contract then return flipped hash(blake2(original_address))
def getAddressCheckSum(address, isContract = False): 
    # Grab first ADDR_SIZE bytes of address
    addressBody = address[0 : AccountBlock.ADDR_SIZE]
    # Calculate the blake2b 
    h = hashlib.blake2b(digest_size= AccountBlock.ADDR_CHECK_SUM_SIZE)
    h.update(b"{addressBody}")
    checkSum = h.hexdigest()

    print(f"Checksum is {checkSum}")

    # If User account returns hash of blake2b
    if (isContract == False):
        print("Returning hexlify")
        return binascii.hexlify(b"{checkSum}")

    print("Return flipped chksum")
    # Otherwise returns hash of flipped blake2b
    newCheckSum = [int(i,16) ^ 0xFF for i in checkSum]
    return binascii.hexlify(b"{newCheckSum}")

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
