# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DGVehicleNitroEffectComponent.py
import weakref
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import IntParam
_DEFAULT_NITRO = 1
_NO_NITRO = 0

@groupComponent(nitro=IntParam(default=_DEFAULT_NITRO))
class DGVehicleNitroEffectComponent(DynamicScriptComponent):

    def __init__(self):
        super(DGVehicleNitroEffectComponent, self).__init__()
        self._appearanceRef = weakref.ref(self.entity.appearance)

    def _onAvatarReady(self):
        super(DGVehicleNitroEffectComponent, self)._onAvatarReady()
        self._setType(self.groupComponentConfig.nitro)

    def onDestroy(self):
        self._setType(_NO_NITRO)
        super(DGVehicleNitroEffectComponent, self).onDestroy()

    def _setType(self, nitro):
        appearance = self._appearanceRef()
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = nitro
        return
