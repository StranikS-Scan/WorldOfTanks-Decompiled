# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AlwaysVisible.py
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class AlwaysVisible(DynamicScriptComponent):

    def _onAvatarReady(self):
        appearance = self.entity.appearance
        if appearance is not None and appearance.findComponentByType(GenericComponents.AlwaysVisible) is None:
            appearance.createComponent(GenericComponents.AlwaysVisible)
        return

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(GenericComponents.AlwaysVisible)
        super(AlwaysVisible, self).onDestroy()
        return
