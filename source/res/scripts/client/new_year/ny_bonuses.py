# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_bonuses.py
import typing
from helpers import dependency
from ny_common.settings import BattleBonusesConsts
from ny_common.BattleBonusesConfig import BattleBonusApplier, BattleBonusesConfig
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import Dict, List, Optional, Callable
CREDITS_BONUS = 'creditsFactor'

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getBonusConfig(lobbyCtx=None):
    return lobbyCtx.getServerSettings().getNewYearBattleBonusConfig()


def getBonusesByType(bonusType):
    config = getBonusConfig()
    return config.getBonusesByType(bonusType)


def getXPBonuses():
    config = getBonusConfig()
    return config.getXPBonuses()


def getCurrencyBonuses():
    config = getBonusConfig()
    return config.getCurrencyBonuses()


def getBonusesChoiceByType(bonusType, choiceID):
    config = getBonusConfig()
    return config.getBonusesChoiceByType(bonusType, choiceID)


def getBonusDependencies():
    config = getBonusConfig()
    return config.getDependencies()


def getBonusTokensDependencies():
    return getBonusDependencies()


def getXpBonusChoise():
    xpBonuses = getXPBonuses()
    if not xpBonuses:
        return {}
    choises = xpBonuses.values()
    return {} if not choises else choises[0][BattleBonusesConsts.CHOOSABLE_BONUS_NAME]


def getXpBonusNameByID(xpBonusID):
    choise = getXpBonusChoise()
    if not choise:
        return ''
    else:
        xpBonusName = ''
        xpBonusByID = choise.get(xpBonusID)
        if xpBonusByID is not None:
            xpBonusName = xpBonusByID.keys()[0]
        return xpBonusName


def getXpBonusIDbyName(xpBonusName):
    choise = getXpBonusChoise()
    for choiseID, bonus in choise.iteritems():
        if xpBonusName in bonus:
            return choiseID

    return None


class EconomicBonusHelper(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getBonusesDataInventory(cls):
        tokens = cls.__itemsCache.items.tokens
        inventoryCounter = lambda dependency: tokens.getTokenCount(dependency) if tokens.isTokenAvailable(dependency) else 0
        return cls.__getBonusesDataByCounter(inventoryCounter)

    @classmethod
    def getMaxBonuses(cls):
        config = getBonusConfig()
        counts = {dependency:None for dependency in config.getDependencies()}
        return cls.__getBonuses(counts)

    @classmethod
    def getBonusesDataByToken(cls, tokenID, index):
        config = getBonusConfig()
        bonusesData = BattleBonusApplier.mergeBonusDataForToken({}, BattleBonusesConsts.CURRENCY_BONUSES, None, config, tokenID, index)
        choise = getXpBonusChoise()
        for choiceID in choise.keys():
            bonusesData = BattleBonusApplier.mergeBonusDataForToken(bonusesData, BattleBonusesConsts.XP_BONUSES, choiceID, config, tokenID, index)

        return bonusesData

    @classmethod
    def __getBonusesDataByCounter(cls, counter):
        config = getBonusConfig()
        counts = BattleBonusApplier.getDependenciesCount(config, counter)
        return cls.__getBonuses(counts)

    @classmethod
    def __getBonuses(cls, counts):
        config = getBonusConfig()
        bonusesData = BattleBonusApplier.mergeBonusData({}, BattleBonusesConsts.CURRENCY_BONUSES, None, config, counts)
        choise = getXpBonusChoise()
        for choiceID in choise.keys():
            bonusesData = BattleBonusApplier.mergeBonusData(bonusesData, BattleBonusesConsts.XP_BONUSES, choiceID, config, counts)

        return bonusesData


def toPrettySingleBonusValue(value):
    return float('{:.1f}'.format(100 * value))


def toPrettyCumulativeBonusValue(value):
    return float('{:.1f}'.format(100 * (value - 1)))


def isBonusApplicable(vehicle, maxReachedLevel):
    return getBonusStatus(vehicle, maxReachedLevel) != BattleBonusesConsts.APPLICABLE


def getBonusStatus(vehicle, maxReachedLevel):
    return BattleBonusApplier.getBonusStatus(BattleBonusesConsts.XP_BONUSES, vehicle.typeDescr if vehicle is not None else None, maxReachedLevel, vehicle.isRented if vehicle is not None else False)
