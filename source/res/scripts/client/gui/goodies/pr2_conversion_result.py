# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/pr2_conversion_result.py
from collections import defaultdict
from typing import TYPE_CHECKING
from debug_utils import LOG_DEBUG
from goodies.pr2_converter import IPR2ConversionDataBridge, PR2Converter, ADVANCED_ITEMS, postConversionByType
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.goodies.goodie_items import Booster

class _PR2ConversionResultDataBridge(IPR2ConversionDataBridge):
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, targetItems):
        super(_PR2ConversionResultDataBridge, self).__init__()
        self.__result = defaultdict(list)
        self.__resultSum = {}
        self.__targetItems = targetItems

    def iterTargetItems(self):
        for oldID, oCount in self.__targetItems:
            yield (oldID, oCount)

    def getItemData(self, uid):
        booster = self.__getBoosterItem(uid)
        return (booster.boosterType, booster.effectTime * booster.effectValue)

    def isAdvancedItem(self, uid):
        return uid in ADVANCED_ITEMS

    def __getBoosterItem(self, uid):
        return self.__goodiesCache.getBooster(uid)

    def applySingleItemsResult(self, resultList):
        newTotalItemsData = defaultdict(lambda : 0)
        for oldID, oldType, oldCount, newID, newCount in resultList:
            booster = self.__getBoosterItem(oldID)
            self.__result[booster.boosterGuiType].append((oldID,
             oldType,
             oldCount,
             newID,
             newCount))
            newTotalItemsData[(oldType, newID)] += newCount

        self.__resultSum = postConversionByType(newTotalItemsData)

    def getResult(self):
        return self.__result

    def getResultSum(self):
        return self.__resultSum


def getConversionDataProvider(data):
    provider = _PR2ConversionResultDataBridge(data)
    PR2Converter().convert(provider)
    return provider


def getConversionResult(data):
    provider = getConversionDataProvider(data)
    return provider.getResult()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def printPR2CachedConversionResult(itemsCache=None):
    printConversionResult(itemsCache.items.goodies.pr2ConversionResult)


def printConversionResult(data):
    result = getConversionResult(data)
    resultStr = '\n'
    for bGUIType, converted in result.iteritems():
        strV = '\n{}:'.format(bGUIType)
        resultStr += strV
        for oldId, _, oldCount, newId, newCount in converted:
            strV = '\n    {} old {} with id={} {} converted to {} new {} with id={}'.format(oldCount, 'items' if oldCount > 1 else 'item', oldId, 'were1' if oldCount > 1 else 'was', newCount, 'items' if newCount > 1 else 'item', newId)
            resultStr += strV

    LOG_DEBUG(resultStr)
