# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffNitroComponent.py
import weakref
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import IntParam
_NITRO_APPEARED = 1
_NITRO_HIDDEN = 0

@groupComponent(nitro=IntParam())
class LSBuffNitroComponent(DynamicScriptComponent):

    def __init__(self):
        super(LSBuffNitroComponent, self).__init__()
        self._appearanceRef = weakref.ref(self.entity.appearance)

    def _onAvatarReady(self):
        super(LSBuffNitroComponent, self)._onAvatarReady()
        nitro = getattr(self.groupComponentConfig, 'nitro', _NITRO_APPEARED)
        self._setType(nitro)

    def onDestroy(self):
        nitroComponents = [ c for c in self.entity.dynamicComponents.values() if isinstance(c, LSBuffNitroComponent) ]
        if len(nitroComponents) <= 1:
            self._setType(_NITRO_HIDDEN)
        super(LSBuffNitroComponent, self).onDestroy()

    def _setType(self, nitro):
        appearance = self._appearanceRef()
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = nitro
        return
