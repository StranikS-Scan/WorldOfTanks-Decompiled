# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventPortal.py
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import HangarVehicleEvent
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class EventPortal(ClientSelectableCameraObject):

    def __init__(self):
        ClientSelectableCameraObject.__init__(self)
        self.__isActivated = False

    def onMouseClick(self):
        g_eventBus.handleEvent(HangarVehicleEvent(HangarVehicleEvent.WT_EVENT_PORTAL_CLICKED, ctx={'data': {}}), EVENT_BUS_SCOPE.LOBBY)

    def onEnterWorld(self, prereqs):
        super(EventPortal, self).onEnterWorld(prereqs)
        self.registerOnMouseClickEvents()
        self.__isActivated = True
        gameEventCtrl = dependency.instance(IGameEventController)
        if gameEventCtrl.isEventPrbActive():
            self.__setCollisionsEnabled(False)

    def onLeaveWorld(self):
        super(EventPortal, self).onLeaveWorld()
        self.unRegisterOnMouseClickEvents()
        self.__isActivated = False

    def setHighlight(self, show):
        isHighlightShown = show and self.enabled
        super(EventPortal, self).setHighlight(isHighlightShown)

    def __wtEventSelected(self, _):
        self.setHighlight(False)
        self.__setCollisionsEnabled(False)

    def __wtEventSelectedOff(self, _):
        self.__setCollisionsEnabled(True)

    def registerOnMouseClickEvents(self):
        self.__addListener(HangarVehicleEvent.WT_EVENT_SELECTED, self.__wtEventSelected)
        self.__addListener(HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.__wtEventSelectedOff)

    def unRegisterOnMouseClickEvents(self):
        self.__removeListener(HangarVehicleEvent.WT_EVENT_SELECTED, self.__wtEventSelected)
        self.__removeListener(HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.__wtEventSelectedOff)

    def __setCollisionsEnabled(self, value):
        if self.collisions is None:
            return
        else:
            if value and not self.__isActivated:
                self.collisions.activate()
            elif not value and self.__isActivated:
                self.collisions.deactivate()
            self.__isActivated = value
            self.setEnable(value)
            return

    def __addListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.LOBBY):
        g_eventBus.addListener(eventType, handler, scope=scope)

    def __removeListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.LOBBY):
        g_eventBus.removeListener(eventType, handler, scope=scope)
