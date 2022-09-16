# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/pr2_converter.py
from math import ceil
XP = 121001
CRED = 121003
XP_CREW_FREE = 121005
XP_DEF = 121000
CRED_DEF = 121002
XP_CREW_FREE_DEF = 121004
ADVANCED_ITEMS = (XP, CRED, XP_CREW_FREE)
_NEW_ID_TO_OLD_IDS = {XP: (5061, 5062, 9015, 9017, 9019, 9021, 9023, 9025, 11001),
 CRED: (9016, 9018, 9020, 9022, 9024, 9026, 111002),
 XP_CREW_FREE: (5028, 5063, 9036, 9038, 5035, 5064, 9035, 9037),
 XP_DEF: tuple(range(5020, 5028)) + (5060, 10001, 10002, 10003),
 CRED_DEF: tuple(range(5042, 5050)) + (5065,),
 XP_CREW_FREE_DEF: tuple(range(5029, 5042)) + (5052, 6002, 6003, 6005) + tuple(range(9027, 9035)) + tuple(range(10011, 10014)) + tuple(range(10021, 10024))}
_OLD_ID_TO_NEW_ID = {oldId:newId for newId, oldItems in _NEW_ID_TO_OLD_IDS.iteritems() for oldId in oldItems}

class BType(object):
    GOLD = 10
    CREDITS = 20
    XP = 30
    CREW_XP = 40
    FREE_XP = 50
    FL_XP = 60
    FREE_XP_CREW_XP = 70


def postConversionByType(convertedByState):
    convertedByNewID = {}
    for (oldType, newBoosterId), newCount in convertedByState.iteritems():
        if oldType in (BType.FREE_XP, BType.CREW_XP):
            savedResult = convertedByNewID.get(newBoosterId, 0)
            if savedResult >= newCount:
                continue
        convertedByNewID[newBoosterId] = newCount

    return convertedByNewID


class IPR2ConversionDataBridge(object):

    def iterTargetItems(self):
        yield
        return

    def getItemData(self, uid):
        raise NotImplementedError

    def isAdvancedItem(self, uid):
        raise NotImplementedError

    def applySingleItemsResult(self, resultList):
        raise NotImplementedError


class PR2Converter(object):

    def convert(self, cDataProvider):
        result = []
        for oldID, oCount in cDataProvider.iterTargetItems():
            oldType, oldWeight = cDataProvider.getItemData(oldID)
            if oldWeight:
                newID, newWeight = self.__getResultConversionData(oldID, cDataProvider)
                if newWeight:
                    result.append((oldID,
                     oldType,
                     oCount,
                     newID,
                     int(ceil(oCount * oldWeight * 1.0 / newWeight))))

        cDataProvider.applySingleItemsResult(result)
        return bool(result)

    def __getResultConversionData(self, oldID, cDataProvider):
        newWeight = 0.0
        newId = _OLD_ID_TO_NEW_ID.get(oldID, 0)
        if newId:
            newWeight = cDataProvider.getItemData(newId)[1]
        return (newId, newWeight)
