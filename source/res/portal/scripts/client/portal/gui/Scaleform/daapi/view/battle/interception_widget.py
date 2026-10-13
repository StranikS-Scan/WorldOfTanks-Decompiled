# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/interception_widget.py
import BigWorld
import Keys
from gui import InputHandler
from PortalVehicleChangeShotComponent import PortalVehicleChangeShotComponent
from portal.gui.Scaleform.daapi.view.meta.PortalInterceptionWidgetMeta import PortalInterceptionWidgetMeta

class InterceptionWidget(PortalInterceptionWidgetMeta):

    def _populate(self):
        super(InterceptionWidget, self)._populate()
        PortalVehicleChangeShotComponent.onControlStarted += self.__onControlStarted
        InputHandler.g_instance.onKeyDown += self.__onKeyDown

    def _dispose(self):
        InputHandler.g_instance.onKeyDown -= self.__onKeyDown
        PortalVehicleChangeShotComponent.onControlStarted -= self.__onControlStarted
        super(InterceptionWidget, self)._dispose()

    def __onControlStarted(self, avatarID, timeLeft):
        if avatarID == BigWorld.player().id:
            self.as_updateTimeS(int(timeLeft))

    def __onKeyDown(self, event):
        isInterruptEvent = event.isKeyDown() and event.key == Keys.KEY_SPACE
        if isInterruptEvent:
            self.__interruptInterception()

    def __interruptInterception(self):
        vehicleChangeComponent = BigWorld.player().DynamicVehicleChangeComponent
        if vehicleChangeComponent.isControllingVehicle:
            vehicleChangeComponent.interruptVehicleControl()
