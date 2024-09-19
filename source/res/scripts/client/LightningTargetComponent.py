# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LightningTargetComponent.py
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class LightningTargetComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        self.__displayEffect(self.isActive)

    def set_isActive(self, _):
        self.__displayEffect(self.isActive)

    def __displayEffect(self, display):
        appearance = self.entity.appearance
        if appearance is None:
            return
        else:
            if display:
                if appearance.findComponentByType(GenericComponents.CarryingLootComponent) is None:
                    appearance.createComponent(GenericComponents.CarryingLootComponent, appearance.gameObject)
            else:
                appearance.removeComponentByType(GenericComponents.CarryingLootComponent)
            return
