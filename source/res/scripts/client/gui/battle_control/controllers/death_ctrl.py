# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/death_ctrl.py
import logging
import BigWorld
import Event
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class DeathScreenController(IArenaVehiclesController, Event.EventsSubscriber):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _SKIP_SCREEN_FOR_TOP_POSITIONS = 0
    _SCREEN_SHOW_DELAY = 0.0

    def __init__(self):
        super(DeathScreenController, self).__init__()
        self.onShowDeathScreen = Event.Event()
        self.onHideDeathScreen = Event.Event()
        self._isShown = False
        self.__delayedCB = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        super(DeathScreenController, self).startControl(battleCtx, arenaVisitor)
        self.subscribeToEvent(self.sessionProvider.shared.vehicleState.onVehicleControlling, self.__onVehicleControlling)
        self.subscribeToEvent(arenaVisitor.getComponentSystem().battleRoyaleComponent.onBattleRoyalePlaceUpdated, self.__onPlayerRankUpdated)

    def stopControl(self):
        try:
            self.__clear()
        except ValueError:
            _logger.warning('Callback has been already deleted, self.__callbackID=%s', str(self.__delayedCB))

        self.unsubscribeFromAllEvents()

    def getControllerID(self):
        return BATTLE_CTRL_ID.DEATH_SCREEN_CTRL

    def __onVehicleControlling(self, _):
        self.__clear()

    def __onPlayerRankUpdated(self, playerRank):
        if not self._isShown and playerRank > 1:
            self.__clear()
            self._isShown = True
            self.__delayedCB = BigWorld.callback(self._SCREEN_SHOW_DELAY, self.__timeToShowHasCome)

    def __timeToShowHasCome(self):
        self.__delayedCB = None
        self.onShowDeathScreen()
        return

    def __clear(self):
        if self.__delayedCB is not None:
            BigWorld.cancelCallback(self.__delayedCB)
            self.__delayedCB = None
        if self._isShown:
            self._isShown = False
            self.onHideDeathScreen()
        return
