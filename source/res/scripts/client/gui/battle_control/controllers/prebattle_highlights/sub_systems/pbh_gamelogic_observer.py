# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/sub_systems/pbh_gamelogic_observer.py
from __future__ import absolute_import
import logging
import typing
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from frameworks_common.state_machine import BaseStateObserver
from gui.battle_control.controllers.prebattle_highlights.sub_systems.base_sub_system import BasePbhSubSystem
from helpers import dependency
from skeletons.gameplay import IGameplayLogic, GameplayStateID, PlayerEventID
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks_common.state_machine import State, StateEvent
_logger = logging.getLogger(__name__)

class PbhGameLogicObserver(BasePbhSubSystem, BaseStateObserver):
    __gameplayLogic = dependency.descriptor(IGameplayLogic)

    def __init__(self, readyCallback):
        self.__stateReached = False
        self.__prebattlePeriodReached = False
        super(PbhGameLogicObserver, self).__init__(readyCallback)

    def subscribe(self):
        self.__gameplayLogic.addStateObserver(self)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def unsubscribe(self):
        self.__gameplayLogic.removeStateObserver(self)
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange

    def isReady(self):
        return self.__stateReached and self.__prebattlePeriodReached

    def startFlow(self):
        pass

    def stopFlow(self):
        pass

    def clear(self):
        self.__stateReached = False
        self.__prebattlePeriodReached = False
        super(PbhGameLogicObserver, self).clear()

    def isObservingState(self, state):
        return state.getStateID() == GameplayStateID.PREBATTLE_HIGHLIGHTS

    def onEnterState(self, state, event):
        _logger.debug('[PBH] PBH game state reached.')
        self.__stateReached = True
        self.__tryCallReadyCallback()

    def postPbhEnd(self):
        self.__gameplayLogic.postStateEvent(PlayerEventID.PREBATTLE_START)
        self.__stateReached = False
        self.__prebattlePeriodReached = False

    def __onArenaPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.PREBATTLE:
            _logger.debug('[PBH] PBH ARENA_PERIOD.PREBATTLE reached.')
            self.__prebattlePeriodReached = True
            self.__tryCallReadyCallback()

    def __tryCallReadyCallback(self):
        if self.isReady() and self._readyCallback is not None:
            self._readyCallback()
        return
