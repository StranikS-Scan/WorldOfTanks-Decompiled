# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_lootsign_ctrl.py
import logging
import Event
from constants import EVENT
from gui.Scaleform.daapi.view.battle.event.markers import LootSignFactory, UIMarkerController
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class LootSignController(IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    LOOT_TYPES = ['ammo_small']

    def __init__(self):
        self.__showLootSign = False
        self._uiMarkerController = UIMarkerController()
        self.__eManager = Event.EventManager()
        self.onLootSignUpdated = Event.Event(self.__eManager)

    @property
    def showLootSign(self):
        return self.__showLootSign

    def startControl(self, battleCtx, arenaVisitor):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl:
            ammoCtrl.onShellsUpdated += self.__onShellsUpdated
            ammoCtrl.onShellsAdded += self.__onShellsAdded
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded += self.__onLootAdded
            lootComp.onLootRemoved += self.__onLootRemoved
        vehicleStateCtrl = self.sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        return

    def stopControl(self):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl:
            ammoCtrl.onShellsUpdated -= self.__onShellsUpdated
            ammoCtrl.onShellsAdded -= self.__onShellsAdded
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded -= self.__onLootAdded
            lootComp.onLootRemoved -= self.__onLootRemoved
        vehicleStateCtrl = self.sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        return

    def __onLootAdded(self, loot):
        if loot.typeName not in self.LOOT_TYPES:
            return
        radius = loot.gameObject.radius
        staticMarker = LootSignFactory.createMarker(loot.position, radius)
        self._uiMarkerController.putMarker(loot.id, staticMarker, radius)

    def __onLootRemoved(self, loot):
        if loot.typeName not in self.LOOT_TYPES:
            return
        self._uiMarkerController.removeMarkerByObjId(loot.id)

    def __onPostMortemSwitched(self, *args):
        self._uiMarkerController.hideMarkers()

    def __onShellsAdded(self, *args):
        self.__toggleLootMarkers()

    def __onShellsUpdated(self, *args):
        self.__toggleLootMarkers()

    def __toggleLootMarkers(self):
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is None:
            return
        else:
            totalAmountOfShells = sum((shell[2] for shell in ammoCtrl.getOrderedShellsLayout()))
            self.__showLootSign = totalAmountOfShells <= EVENT.AMOUNT_OF_SHELLS_SHOW_MARKER
            if self.__showLootSign:
                self._uiMarkerController.showMarkers()
            else:
                self._uiMarkerController.hideMarkers()
            self.onLootSignUpdated()
            return

    def getControllerID(self):
        return BATTLE_CTRL_ID.LOOTSIGN

    def spaceLoadCompleted(self):
        self._uiMarkerController.init()
