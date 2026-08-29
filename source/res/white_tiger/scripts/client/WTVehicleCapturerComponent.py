# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleCapturerComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from GenericComponents import CarryingLootComponent

class WTVehicleCapturerComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        self.set_isCaptureActive(None)
        return

    def set_isCaptureActive(self, prev):
        appearance = self.entity.appearance
        if appearance or appearance.isConstructed:
            if self.isCaptureActive:
                component = appearance.findComponentByType(CarryingLootComponent)
                if not component:
                    appearance.createComponent(CarryingLootComponent, self.entity.entityGameObject)
            else:
                appearance.removeComponentByType(CarryingLootComponent)

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance:
            component = appearance.findComponentByType(CarryingLootComponent)
            if component:
                appearance.removeComponentByType(CarryingLootComponent)
        super(WTVehicleCapturerComponent, self).onDestroy()
