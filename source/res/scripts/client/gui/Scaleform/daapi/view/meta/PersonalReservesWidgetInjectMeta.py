# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalReservesWidgetInjectMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class PersonalReservesWidgetInjectMeta(InjectComponentAdaptor):

    def as_setTargetWidthS(self, value):
        return self.flashObject.as_setTargetWidth(value) if self._isDAAPIInited() else None
