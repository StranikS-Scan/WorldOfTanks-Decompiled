# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FunRandomHangarWidgetMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class FunRandomHangarWidgetMeta(InjectComponentAdaptor):

    def as_setModifiersCountS(self, count):
        return self.flashObject.as_setModifiersCount(count) if self._isDAAPIInited() else None
