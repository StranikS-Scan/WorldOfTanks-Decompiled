# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GFHeaderWidgetMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class GFHeaderWidgetMeta(InjectComponentAdaptor):

    def as_updateMarginsS(self, top, right, left):
        return self.flashObject.as_updateMargins(top, right, left) if self._isDAAPIInited() else None
