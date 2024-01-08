# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_helpers.py
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_tab_model import TabType
import CommandMapping
from gui.Scaleform.daapi.view.common.keybord_helpers import getHotKeyVkList, getHotKeyList
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import time_utils, dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def geFrontlineState(withPrimeTime=False, epicController=None):
    now = time_utils.getCurrentLocalServerTimestamp()
    startDate, endDate = epicController.getSeasonTimeRange()
    if now > endDate:
        season = epicController.getCurrentSeason()
        endSeasonDate = season.getEndDate() if season else 0
        return (FrontlineState.FINISHED, endSeasonDate, int(endSeasonDate - now))
    if now < startDate:
        return (FrontlineState.ANNOUNCE, startDate, int(startDate - now))
    primeTimeStatus, timeLeft, _ = epicController.getPrimeTimeStatus()
    if primeTimeStatus is not PrimeTimeStatus.AVAILABLE:
        if withPrimeTime:
            return (FrontlineState.FROZEN, int(now + timeLeft), timeLeft)
        return (FrontlineState.FROZEN, endDate, int(endDate - now))
    return (FrontlineState.FINISHED, 0, 0) if not epicController.isEnabled() else (FrontlineState.ACTIVE, endDate, int(endDate - now))


def getStatesUnavailableForHangar():
    return [FrontlineState.FINISHED, FrontlineState.ANNOUNCE]


def getProperTabWhileHangarUnavailable():
    frontlineState, _, _ = geFrontlineState()
    return TabType.REWARDS if frontlineState == FrontlineState.FINISHED else None


def getReserveIconPath(icon):
    return 'img://gui/maps/icons/artefact/{}.png'.format(icon)


def getHotKeyListCommands():
    return [CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_LEFT, CommandMapping.CMD_CM_VEHICLE_UPGRADE_PANEL_RIGHT]


def getHotKeyListByIndex(index):
    commands = getHotKeyListCommands()
    return getHotKeyList(commands[index])


def getHotKeyVkListByIndex(index):
    commands = getHotKeyListCommands()
    return getHotKeyVkList(commands[index])


def isHangarAvailable():
    frontlineState, _, _ = geFrontlineState()
    return frontlineState not in getStatesUnavailableForHangar()


class FLBattleTypeDescription(object):
    __epicMetaCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def getDescription(self):
        return self.__getDescription('description')

    def getShortDescription(self):
        return self.__getDescription('shortDescription')

    def getTitle(self):
        return self.__getDescription('title')

    def getBattleTypeIconPath(self, sizeFolder='c_136x136'):
        iconRes = self.__getRI().dyn(sizeFolder).dyn(self.__epicMetaCtrl.getEpicBattlesReservesModifier())
        return backport.image(iconRes()) if iconRes.exists() else ''

    def __getDescription(self, descriptionType):
        modifier = self.__epicMetaCtrl.getEpicBattlesReservesModifier()
        if modifier is None:
            return ''
        else:
            descriptionRes = self.__getRS().dyn(descriptionType).dyn(modifier)
            return backport.text(descriptionRes()) if descriptionRes.exists() else ''

    @staticmethod
    def __getRS():
        return R.strings.fl_common.battleType

    @staticmethod
    def __getRI():
        return R.images.frontline.gui.maps.icons.battleTypes
