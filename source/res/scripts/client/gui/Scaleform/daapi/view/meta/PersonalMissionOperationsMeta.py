# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionOperationsMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionOperationsMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onOperationClick(self, pmType, operationID):
        self._printOverrideError('onOperationClick')

    def showInfo(self):
        self._printOverrideError('showInfo')

    def as_setOperationsS(self, operations):
        return self.flashObject.as_setOperations(operations) if self._isDAAPIInited() else None

    def as_setTitleS(self, titleVO):
        return self.flashObject.as_setTitle(titleVO) if self._isDAAPIInited() else None
