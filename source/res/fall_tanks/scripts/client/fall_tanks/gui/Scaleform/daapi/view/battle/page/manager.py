# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/page/manager.py
import typing
import weakref
from enum import Enum
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
if typing.TYPE_CHECKING:
    from fall_tanks.gui.Scaleform.daapi.view.battle.page import FallTanksPage
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo

class FallTanksBattleState(Enum):
    LOADING = 'loading'
    PLAYER_IN_RACE = 'playerInRace'
    PLAYER_IN_RESPAWN = 'playerInRespawn'
    PLAYER_FINISHED = 'playerFinished'
    OBSERVER = 'observer'


class FallTanksComponentsManager(object):
    __slots__ = ('__page', '__state', '__isBattleLoaded', '__isInPostmortem', '__isVehicleFinished', '__isPlayerVehicle')
    _COMPONENTS_VISIBILITY = {FallTanksBattleState.LOADING: (set(), set()),
     FallTanksBattleState.PLAYER_IN_RACE: ({BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL}, {BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL}),
     FallTanksBattleState.PLAYER_IN_RESPAWN: ({BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL}, {BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL}),
     FallTanksBattleState.PLAYER_FINISHED: (set(), {BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL}),
     FallTanksBattleState.OBSERVER: ({BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL}, {BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL})}

    def __init__(self, page):
        self.__page = weakref.proxy(page)
        self.__state = FallTanksBattleState.LOADING
        self.__isBattleLoaded = False
        self.__isInPostmortem = False
        self.__isVehicleFinished = False
        self.__isPlayerVehicle = True

    def clear(self):
        self.__state = FallTanksBattleState.LOADING
        self.__isBattleLoaded = False
        self.__isInPostmortem = False
        self.__isVehicleFinished = False
        self.__isPlayerVehicle = True

    def destroy(self):
        self.__page = None
        self.clear()
        return

    def onBattleLoaded(self):
        self.__isBattleLoaded = True
        self.__invalidateBattleState()

    def setIsInPostmortem(self, isInPostmortem):
        self.__isInPostmortem = isInPostmortem
        self.__invalidateBattleState()

    def onFallTanksAttachedInfoUpdate(self, attachedInfo):
        self.__isVehicleFinished = attachedInfo.isFinished
        self.__isPlayerVehicle = attachedInfo.isPlayerVehicle
        self.__invalidateBattleState()

    def __getBattleState(self):
        if not self.__isBattleLoaded:
            return FallTanksBattleState.LOADING
        if not self.__isInPostmortem:
            return FallTanksBattleState.PLAYER_IN_RACE
        if not self.__isPlayerVehicle:
            return FallTanksBattleState.OBSERVER
        return FallTanksBattleState.PLAYER_IN_RESPAWN if not self.__isVehicleFinished else FallTanksBattleState.PLAYER_FINISHED

    def __invalidateBattleState(self):
        self.__state, oldState = self.__getBattleState(), self.__state
        if self.__state != oldState and self.__page is not None:
            visible, hidden = self._COMPONENTS_VISIBILITY[self.__state]
            self.__page.setComponentsVisibility(visible, hidden)
        return
