# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DAAPISimpleContainerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class DAAPISimpleContainerMeta(BaseDAAPIModule):

    def as_populateS(self):
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None
