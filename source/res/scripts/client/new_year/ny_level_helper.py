# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_level_helper.py
import typing
import logging
from gui.server_events.recruit_helper import getRecruitInfo
from gui.server_events.bonuses import SimpleBonus
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from items import ny19
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

def getLevelIndexes():
    for index in xrange(ny19.CONSTS.MIN_ATMOSPHERE_LEVEL, ny19.CONSTS.MAX_ATMOSPHERE_LEVEL + 1):
        yield index


class NewYearAtmospherePresenter(object):

    @staticmethod
    def getFloatLevelProgress():
        levelProgress, bound = ny19.getAtmosphereProgress(NewYearAtmospherePresenter.getAmount())
        return float(levelProgress) / bound

    @staticmethod
    def getLevel():
        return ny19.getAtmosphereLevel(NewYearAtmospherePresenter.getAmount())

    @staticmethod
    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getAmount(itemsCache=None):
        slots = itemsCache.items.festivity.getSlots()
        return ny19.getTotalAtmosphere(slots)


class LevelInfo(object):
    __slots__ = ('__level', '__bonuses', '__tankmanInfo', '__tankmanToken', '__vehicle', '__questID', '__variadicDiscount')
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, level):
        self.__level = level
        self.__bonuses = []
        self.__tankmanInfo = None
        self.__tankmanToken = None
        self.__vehicle = None
        self.__questID = findFirst(lambda x: x.level == level, ny19.g_cache.levels.values()).id
        self.__variadicDiscount = findFirst(lambda x: x.level == level, ny19.g_cache.variadicDiscounts.values())
        self.__bonusProccesing()
        return

    def isCurrent(self):
        return self.__level == NewYearAtmospherePresenter.getLevel()

    def isAchieved(self):
        return self.__level <= self._itemsCache.items.festivity.getMaxLevel()

    def isLastLevel(self):
        return self.__level == ny19.CONSTS.MAX_ATMOSPHERE_LEVEL

    def isQuestCompleted(self):
        levelQuest = self._eventsCache.getQuestByID(self.__questID)
        return False if levelQuest is None else levelQuest.isCompleted()

    def level(self):
        return self.__level

    def variadicDiscountID(self):
        return self.__variadicDiscount.id

    def discountApplied(self):
        if self.__vehicle is not None:
            return True
        else:
            tokens = self._itemsCache.items.tokens.getTokens()
            return True if self.isAchieved() and self.isQuestCompleted() and self.__variadicDiscount is not None and self.__variadicDiscount.id not in tokens else False

    def getVehiclesByDiscount(self):
        result = {}
        if self.__variadicDiscount is None:
            return result
        else:
            leftRange, rightRange = self.__variadicDiscount.goodiesRange
            vehicleDiscounts = self._itemsCache.items.shop.getVehicleDiscountDescriptions()
            for discountID in xrange(leftRange, rightRange + 1):
                if discountID in vehicleDiscounts:
                    discount = vehicleDiscounts[discountID]
                    result[discount.target.targetValue] = discountID

            return result

    def getSelectedVehicle(self):
        if self.__vehicle is not None:
            return self.__vehicle
        else:
            if self.discountApplied():
                selectedDiscounts = self._itemsCache.items.festivity.getSelectedDiscounts()
                leftRange, rightRange = self.__variadicDiscount.goodiesRange
                vehicleDiscounts = self._itemsCache.items.shop.getVehicleDiscountDescriptions()
                for discountID in xrange(leftRange, rightRange + 1):
                    if discountID in vehicleDiscounts and discountID in selectedDiscounts:
                        discount = vehicleDiscounts[discountID]
                        return self._itemsCache.items.getItemByCD(discount.target.targetValue)

            return

    def hasGiftedVehicle(self):
        return True if self.__vehicle is not None else False

    def hasTankman(self):
        return self.__tankmanToken is not None

    def tankmanIsRecruited(self):
        if self.isAchieved() and self.isQuestCompleted() and self.hasTankman():
            tokens = self._itemsCache.items.tokens.getTokens()
            return self.__tankmanToken not in tokens
        return False

    def getTankmanToken(self):
        return self.__tankmanToken

    def getTankmanInfo(self):
        return self.__tankmanInfo

    def variadicDiscountValue(self):
        if self.__variadicDiscount is None:
            return
        else:
            variadicDiscount = self.__variadicDiscount
            leftRange, rightRange = variadicDiscount.goodiesRange
            vehicleDiscounts = self._itemsCache.items.shop.getVehicleDiscountDescriptions()
            for discountID in xrange(leftRange, rightRange + 1):
                if discountID in vehicleDiscounts:
                    discount = vehicleDiscounts[discountID]
                    return discount.resource.value

            _logger.warning('Vehicle discount has not been found in %s level', self.__level)
            return

    def getBonuses(self):
        return self.__bonuses

    def updateBonuses(self):
        if not self.__bonuses:
            self.__bonusProccesing()

    def __bonusProccesing(self):
        levelQuest = self._eventsCache.getQuestByID(self.__questID)
        if levelQuest is None:
            return
        else:
            for bonus in levelQuest.getBonuses():
                if bonus.getName() == 'vehicles':
                    self.__vehicle = bonus.getVehicles()[0][0]
                if bonus.getName() == 'tmanToken':
                    for tokenID in bonus.getTokens():
                        recruitInfo = getRecruitInfo(tokenID)
                        if recruitInfo is not None:
                            self.__tankmanInfo = recruitInfo
                            self.__tankmanToken = tokenID

                self.__bonuses.append(bonus)

            return
