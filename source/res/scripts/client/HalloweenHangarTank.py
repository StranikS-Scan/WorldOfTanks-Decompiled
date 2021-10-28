# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HalloweenHangarTank.py
import logging
import BigWorld
from items import vehicles
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
_logger = logging.getLogger(__name__)

class HalloweenHangarTank(ClientSelectableCameraObject):
    hangarSpace = dependency.descriptor(IHangarSpace)
    _PREVIEW_PANELS = (VEHPREVIEW_CONSTANTS.PROGRESSION_STYLES_BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.TRADE_IN_BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.PERSONAL_TRADE_IN_BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.OFFER_GIFT_BUYING_PANEL_PY_ALIAS)

    def __init__(self):
        super(HalloweenHangarTank, self).__init__()
        self.typeDescriptor = None
        self.markerStyleId = 1
        return

    def onEnterWorld(self, prereqs):
        super(HalloweenHangarTank, self).onEnterWorld(prereqs)
        self.typeDescriptor = vehicles.VehicleDescr(typeName=self.vehicleType)
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentsRegistered)
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentsUnregistered)
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HALLOWEEN_TANK_LOADED, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onLeaveWorld(self):
        super(HalloweenHangarTank, self).onLeaveWorld()
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentsRegistered)
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentsUnregistered)
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HALLOWEEN_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onSelect(self):
        super(HalloweenHangarTank, self).onSelect()
        camera = self.hangarSpace.space.camera
        camera.setStaticCollisions(self.cameraStaticCollisions)
        if self.collisions is not None:
            BigWorld.appendCameraCollider((self.collisions.getColliderID(), (0,)))
        return

    def onDeselect(self, newSelectedObject):
        super(HalloweenHangarTank, self).onDeselect(newSelectedObject)
        camera = self.hangarSpace.space.camera
        camera.setStaticCollisions(True)
        if self.collisions is not None:
            BigWorld.removeCameraCollider(self.collisions.getColliderID())
        return

    def __onComponentsRegistered(self, event):
        if event.alias in self._PREVIEW_PANELS:
            self.setEnable(False)

    def __onComponentsUnregistered(self, event):
        if event.alias in self._PREVIEW_PANELS:
            self.setEnable(True)
