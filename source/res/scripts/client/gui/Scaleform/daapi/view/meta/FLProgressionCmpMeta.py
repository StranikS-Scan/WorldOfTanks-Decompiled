# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FLProgressionCmpMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class FLProgressionCmpMeta(InjectComponentAdaptor):

    def as_updateVisibilityS(self, isVisible):
        return self.flashObject.as_updateVisibility(isVisible) if self._isDAAPIInited() else None
