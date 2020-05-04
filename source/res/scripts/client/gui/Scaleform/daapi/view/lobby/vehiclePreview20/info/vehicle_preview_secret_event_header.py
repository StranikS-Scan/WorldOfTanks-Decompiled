# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_secret_event_header.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.secret_event.action_menu_widget import ActionMenuWidget

class VehiclePreviewSecretEventHeader(InjectComponentAdaptor):
    __slots__ = ()

    def _makeInjectView(self):
        return ActionMenuWidget()

    def handleEscape(self):
        self.injectedView.handleEscape()
