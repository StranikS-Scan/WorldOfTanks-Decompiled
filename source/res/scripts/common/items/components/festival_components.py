# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/festival_components.py
from constants import IS_CLIENT, IS_WEB
from items.components.festival_constants import FEST_ITEM_TYPE, FEST_ITEM_QUALITY, FEST_TYPE_IDS, FEST_INVALID_COST, MAX_FESTIVAL_ITEM_ID
from soft_exception import SoftException

class FestivalItemDescriptor(object):
    _CLIENT_RES_ID = 'resId'
    _CLIENT_ALT_RES_IDS = 'altResIds'
    _CLIENT_WEIGHT = 'weight'
    __slots__ = ('__id', '__type', '__quality', '__clientCfg', '__cost')

    def __init__(self, itemID, itemType, quality, cost, clientCfg):
        self.__id = itemID
        self.__type = itemType
        self.__quality = quality
        self.__clientCfg = clientCfg
        self.__cost = cost

    def getID(self):
        return self.__id

    def getResId(self):
        return self.__clientCfg.get(self._CLIENT_RES_ID, '')

    def getAltResIds(self):
        return self.__clientCfg.get(self._CLIENT_ALT_RES_IDS, {})

    def getWeight(self):
        return self.__clientCfg.get(self._CLIENT_WEIGHT, 0)

    def getType(self):
        return self.__type

    def isAllowedToBuy(self):
        return self.__cost != FEST_INVALID_COST

    def getTypeID(self):
        return FEST_TYPE_IDS[self.__type]

    def getQuality(self):
        return self.__quality

    def getCost(self):
        return self.__cost

    @classmethod
    def createItemBySection(cls, section):
        itemID = section.readInt('id')
        if itemID < 0 or itemID > MAX_FESTIVAL_ITEM_ID:
            raise SoftException('Invalid festival item id - %d' % itemID)
        itemType = section.readString('type')
        if itemType not in FEST_ITEM_TYPE.ALL:
            raise SoftException("Wrong type of Festival item - '%s'" % itemType)
        quality = section.readString('quality')
        if quality not in FEST_ITEM_QUALITY.ALL:
            raise SoftException("Wrong quality of Festival item - '%s'" % quality)
        cost = section.readInt('cost', FEST_INVALID_COST)
        if quality == FEST_ITEM_QUALITY.COMMON and cost <= 0:
            raise SoftException("Don't set or invalid cost value in item(itemID - %s)" % itemID)
        clientCfg = {}
        if IS_CLIENT or IS_WEB:
            clientCfg[cls._CLIENT_RES_ID] = section.readString('resId')
            listAltItemID = section.readString('altItemIDs').split()
            listAltResId = section.readString('altResIds').split()
            if len(listAltItemID) != len(listAltResId):
                raise SoftException('Length of altItemIDs and altResIds not equal')
            altResIdsResult = {}
            for ind, resId in enumerate(listAltResId):
                altItemID = int(listAltItemID[ind])
                if altItemID in altResIdsResult:
                    raise SoftException('Duplicate itemID in altItemIds(itemID - %s)' % altItemID)
                altResIdsResult[altItemID] = resId

            clientCfg[cls._CLIENT_ALT_RES_IDS] = altResIdsResult
            clientCfg[cls._CLIENT_WEIGHT] = section.readFloat(cls._CLIENT_WEIGHT)
        return cls(itemID=itemID, itemType=itemType, quality=quality, cost=cost, clientCfg=clientCfg)


class ProgressRewardDescriptor(object):
    __slots__ = ('__tokenID', '__reachValue', '__showRewards')

    def __init__(self, tokenID, reachValue, showRewards):
        self.__tokenID = tokenID
        self.__reachValue = reachValue
        self.__showRewards = showRewards

    def getTokenID(self):
        return self.__tokenID

    def getReachValue(self):
        return self.__reachValue

    def getShowRewards(self):
        return self.__showRewards

    @classmethod
    def createItemBySection(cls, section):
        tokenID = section.readString('tokenID')
        reachValue = section.readInt('reachValue')
        showRewards = section.readBool('showRewards', True)
        return cls(tokenID, reachValue, showRewards)
