# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SE22EntryPointMeta.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class SE22EntryPointMeta(InjectComponentAdaptor):

    def setIsNewS(self, value):
        return self.flashObject.setIsNew(value) if self._isDAAPIInited() else None
