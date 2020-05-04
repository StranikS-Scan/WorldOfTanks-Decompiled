# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/epic_maps_ctrl.py
import Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
import CommandMapping
from gui.battle_control import event_dispatcher as gui_event_dispatcher
import Math

class MapsController(IViewComponentsController):

    def __init__(self, setup):
        super(MapsController, self).__init__()
        self.__plugins = {}
        self.__overviewMapUi = None
        self.__miniMapUi = None
        self.__eManager = Event.EventManager()
        self.__isOverlayActive = True
        self.__overviewMapScreenVisible = False
        self.__savedToggleState = False
        self.onOverlayTriggered = Event.Event(self.__eManager)
        self.onVisibilityChanged = Event.Event(self.__eManager)
        return

    def setViewComponents(self, *components):
        if len(components) >= 2:
            self.__overviewMapUi = components[0]
            self.__miniMapUi = components[1]
            self.__overviewMapUi.start()
        else:
            self.__miniMapUi = components[0]

    def getControllerID(self):
        return BATTLE_CTRL_ID.MAPS

    def startControl(self):
        pass

    def stopControl(self):
        self.__eManager.clear()
        self.__eManager = None
        return

    def clearViewComponents(self):
        self.__overviewMapUi = None
        self.__miniMapUi = None
        return

    def getMinimapZoomMode(self):
        return self.__miniMapUi.getZoomMode() if self.__miniMapUi is not None else 1

    def getMinimapCenterPosition(self):
        return self.__miniMapUi.getCenterPosition() if self.__miniMapUi is not None else Math.Vector3(0, 0, 0)

    def getVehiclePosition(self, vID):
        return self.__miniMapUi.getPositionOfEntry(vID) if self.__miniMapUi is not None else Math.Vector3(-99999.9, -99999.9, -99999.9)

    def overlayTriggered(self, isActive):
        self.__isOverlayActive = isActive
        self.onOverlayTriggered(self.__isOverlayActive)

    @property
    def overlayActive(self):
        return self.__isOverlayActive

    @property
    def overviewMapScreenVisible(self):
        return self.__overviewMapScreenVisible

    def setOverviewMapScreenVisibility(self, isVisible):
        if isVisible == self.__overviewMapScreenVisible:
            return
        self.__overviewMapScreenVisible = isVisible
        self.onVisibilityChanged(isVisible)
        if isVisible:
            self.overlayTriggered(True)

    def overviewMapTriggered(self):
        gui_event_dispatcher.setMinimapCmd(CommandMapping.g_instance.get('CMD_MINIMAP_VISIBLE'))
