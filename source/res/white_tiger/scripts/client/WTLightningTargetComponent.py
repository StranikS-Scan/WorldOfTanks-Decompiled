# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTLightningTargetComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from WhiteTigerComponents import WTCaptureLightningFilterComponent

class WTLightningTargetComponent(DynamicScriptComponent):

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
                if appearance.findComponentByType(WTCaptureLightningFilterComponent) is None:
                    appearance.createComponent(WTCaptureLightningFilterComponent)
            else:
                appearance.removeComponentByType(WTCaptureLightningFilterComponent)
            return
