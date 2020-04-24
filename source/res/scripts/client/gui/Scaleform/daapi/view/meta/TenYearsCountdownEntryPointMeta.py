# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TenYearsCountdownEntryPointMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class TenYearsCountdownEntryPointMeta(InjectComponentAdaptor):

    def as_updateActivityS(self, isStageActive):
        return self.flashObject.as_updateActivity(isStageActive) if self._isDAAPIInited() else None

    def as_setAnimationEnabledS(self, isEnabled):
        return self.flashObject.as_setAnimationEnabled(isEnabled) if self._isDAAPIInited() else None
