# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AlwaysVisible.py
import ArenaComponents
from script_component.ScriptComponent import DynamicScriptComponent

class AlwaysVisible(DynamicScriptComponent):

    def __init__(self):
        super(AlwaysVisible, self).__init__()
        appearance = self.entity.appearance
        if appearance is not None and appearance.findComponentByType(ArenaComponents.AlwaysVisible) is None:
            appearance.createComponent(ArenaComponents.AlwaysVisible)
        return

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(ArenaComponents.AlwaysVisible)
        super(AlwaysVisible, self).onDestroy()
        return
