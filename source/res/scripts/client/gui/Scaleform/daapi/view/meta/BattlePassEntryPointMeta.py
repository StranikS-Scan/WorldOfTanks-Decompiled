# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattlePassEntryPointMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class BattlePassEntryPointMeta(InjectComponentAdaptor):

    def setIsSmall(self, value):
        self._printOverrideError('setIsSmall')

    def as_setIsMouseEnabledS(self, value):
        return self.flashObject.as_setIsMouseEnabled(value) if self._isDAAPIInited() else None
