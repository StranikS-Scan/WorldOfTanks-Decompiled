# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PMOldOperationsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PMOldOperationsMeta(BaseDAAPIComponent):

    def onOperationClick(self, pmType, operationID):
        self._printOverrideError('onOperationClick')

    def showInfo(self):
        self._printOverrideError('showInfo')

    def as_setOperationsS(self, operations):
        return self.flashObject.as_setOperations(operations) if self._isDAAPIInited() else None

    def as_setTitleS(self, titleVO):
        return self.flashObject.as_setTitle(titleVO) if self._isDAAPIInited() else None
