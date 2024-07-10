# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/platoon/platoon_helpers.py
import logging
from collections import namedtuple
from UnitBase import BitfieldHelper
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from frameworks.wulf import WindowFlags, WindowLayer
from gui.Scaleform.locale.PLATOON import PLATOON
from gui.impl.pub import WindowImpl
from helpers import dependency
from helpers import i18n
from items import vehicles
from shared_utils import BitmaskHelper
from skeletons.gui.game_control import IPlatoonController, IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
Position = namedtuple('Position', ['x', 'y'])

class PreloadableWindow(WindowImpl):

    def __init__(self, wndFlags=WindowFlags.UNDEFINED, content=None, layer=WindowLayer.UNDEFINED):
        super(PreloadableWindow, self).__init__(wndFlags, content=content, layer=layer)
        self.__preload = False

    def preload(self):
        self.__preload = True
        super(PreloadableWindow, self).load()

    def _isPreloading(self):
        return self.__preload

    def _onContentReady(self):
        super(PreloadableWindow, self)._onContentReady()
        if self.__preload:
            self.__preload = False
            self.hide()


def removeNationFromTechName(string):
    result = string.split(':')
    if len(result) > 1:
        return result[1]
    return result[0] if result else ''


def getNationFromTechName(string):
    result = string.split(':')
    return result[0] if result else ''


def convertTierFilterToList(tierFilter):
    tierFilterArray = []
    unitFilter = BitfieldHelper(tierFilter)
    for bit in range(1, 11):
        if unitFilter.isSetBit(bit):
            tierFilterArray.append(bit)

    return tierFilterArray


def isExpandedTierFilter(unitFilter, tierFilterList):
    return convertTierFilterToList(unitFilter) != tierFilterList


def getVehicleDescriptorByIntCD(vehicleIntCD):
    _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
    return vehicles.VehicleDescr(typeID=(nationId, itemId))


def getQueueInfoByQueueType(queueInfo, queueType):
    defaultQueueInfo = {'numInQueue': 0}
    return queueInfo.get(queueType, defaultQueueInfo) if queueInfo else defaultQueueInfo


def formatSearchEstimatedTime(seconds):
    if seconds > 60 or seconds < 1:
        return i18n.makeString(PLATOON.SEARCHING_ESTIMATED_MORETHAN) % {'seconds': 60}
    if seconds <= 5:
        seconds = 5
    elif seconds <= 10:
        seconds = 10
    elif seconds <= 15:
        seconds = 15
    elif seconds <= 20:
        seconds = 20
    elif seconds <= 30:
        seconds = 30
    else:
        seconds = 60
    return i18n.makeString(PLATOON.SEARCHING_ESTIMATED_LESSTHAN) % {'seconds': seconds}


class BonusState(BitmaskHelper):
    NO_BONUS = 0
    XP_BONUS = 1
    SQUAD_CREDITS_BONUS = 2
    PREM_CREDITS_BONUS = 4


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, hangarGuiCtrl=IHangarGuiController, platoonCtrl=IPlatoonController)
def getPlatoonBonusState(isPlatoonCreated, lobbyCtx=None, hangarGuiCtrl=None, platoonCtrl=None):
    bonusState = BonusState.NO_BONUS
    if lobbyCtx.getServerSettings().squadPremiumBonus.isEnabled:
        if hangarGuiCtrl.checkCurrentBonusCaps(_CAPS.PREM_SQUAD_CREDITS):
            if isPlatoonCreated:
                playerInfo = platoonCtrl.getPlayerInfo()
                if playerInfo and playerInfo.hasPremium:
                    bonusState = BonusState.addIfNot(bonusState, BonusState.PREM_CREDITS_BONUS)
                if platoonCtrl.isUnitWithPremium():
                    bonusState = BonusState.addIfNot(bonusState, BonusState.SQUAD_CREDITS_BONUS)
            else:
                bonusState = BonusState.addIfNot(bonusState, BonusState.PREM_CREDITS_BONUS)
                bonusState = BonusState.addIfNot(bonusState, BonusState.SQUAD_CREDITS_BONUS)
    if hangarGuiCtrl.checkCurrentBonusCaps(_CAPS.SQUAD_XP):
        bonusState = BonusState.addIfNot(bonusState, BonusState.XP_BONUS)
    return bonusState
