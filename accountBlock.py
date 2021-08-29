from common import Common

class AccountBlock:

    blockType = 0
    height = 0
    hash = ""
    previousHash = ""
    address = ""
    publicKey = ""
    toAddress = ""
    tokenId = ""
    amount = 0
    data = ""
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

    # Converts account block to a hash
    def toHash(self):

        hash = ""
        return hash