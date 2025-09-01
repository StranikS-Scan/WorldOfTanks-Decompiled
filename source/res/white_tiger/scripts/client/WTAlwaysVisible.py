# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTAlwaysVisible.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from WhiteTigerComponents import WTAlwaysVisibleComponent

class WTAlwaysVisible(DynamicScriptComponent):

    def _onAvatarReady(self):
        appearance = self.entity.appearance
        if appearance is not None and appearance.findComponentByType(WTAlwaysVisibleComponent) is None:
            appearance.createComponent(WTAlwaysVisibleComponent)
        return

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(WTAlwaysVisibleComponent)
        super(WTAlwaysVisible, self).onDestroy()
        return
