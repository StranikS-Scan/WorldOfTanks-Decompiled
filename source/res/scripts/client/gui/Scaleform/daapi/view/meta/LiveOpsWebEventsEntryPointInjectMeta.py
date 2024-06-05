# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LiveOpsWebEventsEntryPointInjectMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class LiveOpsWebEventsEntryPointInjectMeta(InjectComponentAdaptor):

    def as_setIsSmallS(self, isSmall):
        return self.flashObject.as_setIsSmall(isSmall) if self._isDAAPIInited() else None
