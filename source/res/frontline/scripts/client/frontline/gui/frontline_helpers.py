# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_helpers.py
import CommandMapping
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_tab_model import TabType
from frontline_common.frontline_constants import RESERVES_MODIFIER_NAMES
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

    @staticmethod
    def getDescription(reservesModifier=None):
        return FLBattleTypeDescription.__getDescription('description', reservesModifier)

    @staticmethod
    def getShortDescription(reservesModifier=None):
        return FLBattleTypeDescription.__getDescription('shortDescription', reservesModifier)

    @staticmethod
    def getTitle(reservesModifier=None):
        return FLBattleTypeDescription.__getDescription('title', reservesModifier)

    @staticmethod
    def getBattleTypeIconPath(reservesModifier=None, sizeFolder='c_136x136'):
        if reservesModifier is None:
            return ''
        else:
            modifier = RESERVES_MODIFIER_NAMES[reservesModifier]
            iconRes = FLBattleTypeDescription.__getRI().dyn(sizeFolder).dyn(modifier)
            return backport.image(iconRes()) if iconRes.exists() else ''

    @staticmethod
    def __getDescription(descriptionType, reservesModifier):
        if reservesModifier is None:
            return ''
        else:
            modifier = RESERVES_MODIFIER_NAMES[reservesModifier]
            descriptionRes = FLBattleTypeDescription.__getRS().dyn(descriptionType).dyn(modifier)
            return backport.text(descriptionRes()) if descriptionRes.exists() else ''

    @staticmethod
    def __getRS():
        return R.strings.fl_common.battleType

    @staticmethod
    def __getRI():
        return R.images.frontline.gui.maps.icons.battleTypes
