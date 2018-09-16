# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/BaseDAAPIModuleMeta.py
from gui.Scaleform.framework.entities.DAAPIEntity import DAAPIEntity

class BaseDAAPIModuleMeta(DAAPIEntity):

    def as_populateS(self):
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None
