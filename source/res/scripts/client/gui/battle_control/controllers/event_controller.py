# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_controller.py
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS

class EventController(IArenaVehiclesController):
    __slots__ = ('__markersManager', '__uiMarkerController')

    def __init__(self, setup):
        super(EventController, self).__init__()
        self.__markersManager = None
        self.__uiMarkerController = None
        if BONUS_CAPS.checkAny(setup.arenaEntity.bonusType, BONUS_CAPS.EVENT_POINTS_PICKUP_MECHANICS):
            from event_mode.markers import EventMarkersManager, UIMarkerController
            self.__uiMarkerController = UIMarkerController()
            self.__markersManager = EventMarkersManager()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_VIEW

    def setMarkersVisible(self, visible):
        if self.__uiMarkerController:
            self.__uiMarkerController.setVisible(visible)

    def spaceLoadCompleted(self):
        if self.__markersManager:
            self.__uiMarkerController.init()
            self.__markersManager.init(self.__uiMarkerController)
