# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RtsMetaWidgetMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class RtsMetaWidgetMeta(InjectComponentAdaptor):

    def as_setSparkVisibleS(self, value):
        return self.flashObject.as_setSparkVisible(value) if self._isDAAPIInited() else None
