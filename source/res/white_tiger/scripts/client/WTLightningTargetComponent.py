# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTLightningTargetComponent.py
from __future__ import absolute_import
import CGF
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
        appearanceGo = appearance.gameObject if appearance is not None else None
        if appearanceGo is None:
            return
        else:
            if display:
                if not appearanceGo.hasComponent(WTCaptureLightningFilterComponent):
                    queue = CGF.CommandQueue(appearanceGo.spaceID)
                    queue.createComponent(appearanceGo, WTCaptureLightningFilterComponent)
            else:
                appearanceGo.removeComponent(WTCaptureLightningFilterComponent)
            return
