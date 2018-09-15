# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionOperationsPageMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionOperationsPageMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def showAwards(self):
        self._printOverrideError('showAwards')

    def showInfo(self):
        self._printOverrideError('showInfo')

    def onOperationClick(self, operationID):
        self._printOverrideError('onOperationClick')

    def as_setDataS(self, data):
        """
        :param data: Represented by OperationsPageVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
