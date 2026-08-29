# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleAlwaysVisible.py
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class WTVehicleAlwaysVisible(DynamicScriptComponent):

    def _onAvatarReady(self):
        appearance = self.entity.appearance
        if appearance or appearance.isConstructed:
            if not appearance.findComponentByType(GenericComponents.AlwaysVisible):
                appearance.createComponent(GenericComponents.AlwaysVisible)

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(GenericComponents.AlwaysVisible)
        super(WTVehicleAlwaysVisible, self).onDestroy()
        return
