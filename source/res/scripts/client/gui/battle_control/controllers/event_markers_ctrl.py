# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_markers_ctrl.py
import weakref
import logging
from Event import Event
from helpers import dependency
from constants import ECP_HUD_INDEXES, ECP_HUD_TOGGLES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class EventMarkersController(IArenaVehiclesController, GameEventGetterMixin):

    class Events(object):

        def __init__(self):
            super(EventMarkersController.Events, self).__init__()
            self.onECPAdded = Event()
            self.onECPRemoved = Event()
            self.onECPUpdated = Event()

    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        GameEventGetterMixin.__init__(self)
        self._events = self.Events()
        self.__arenaVisitor = weakref.proxy(setup.arenaVisitor)
        self.__soulsOnCollector = 0
        self.__capacityOnCollector = 0

    @property
    def events(self):
        return self._events

    def startControl(self, battleCtx, arenaVisitor):
        ecpComp = getattr(self.__arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] += self.__onECPAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] += self.__onECPRemoved
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer += self.__onECPUpdated
        return

    def stopControl(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onUpdateScenarioTimer -= self.__onECPUpdated
        ecpComp = getattr(self.__arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.on] -= self.__onECPAdded
            ecpComp.ecpHUDEvents[ECP_HUD_INDEXES.marker][ECP_HUD_TOGGLES.off] -= self.__onECPRemoved
        return

    def getECPPositionsIterator(self):
        ecpComp = getattr(self.__arenaVisitor.getComponentSystem(), 'ecp', None)
        if ecpComp is not None:
            ecpCompEntities = ecpComp.getECPEntities()
            for ecp in ecpCompEntities.values():
                yield (ecp.id, ecp.position, ecp.minimapSymbol)

        return

    def __onECPAdded(self, ecp):
        battleGoals = self.sessionProvider.dynamic.battleGoals
        if battleGoals:
            self.__soulsOnCollector = 0
            self.__capacityOnCollector = 0
        self.events.onECPAdded(ecp=ecp)

    def __onECPUpdated(self, waitTime, alarmTime, isVisible):
        battleGoals = self.sessionProvider.dynamic.battleGoals
        if battleGoals:
            progress = battleGoals.getCurrentCollectorSoulsInfo()
            self.events.onECPUpdated(progress=progress)

    def __onECPRemoved(self, ecp):
        self.events.onECPRemoved(ecp=ecp)

    def getControllerID(self):
        return BATTLE_CTRL_ID.WORLD_MARKERS
