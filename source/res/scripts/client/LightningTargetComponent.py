# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LightningTargetComponent.py
from GenericComponents import CarryingLootComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent

class LightningTargetComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.createComponent(CarryingLootComponent, self.entity.entityGameObject)
        return

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(CarryingLootComponent)
        super(LightningTargetComponent, self).onDestroy()
        return
