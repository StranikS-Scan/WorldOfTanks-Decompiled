# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FunRandomNYHangarWidgetMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class FunRandomNYHangarWidgetMeta(InjectComponentAdaptor):

    def as_updateHitAreaS(self):
        return self.flashObject.as_updateHitArea() if self._isDAAPIInited() else None
