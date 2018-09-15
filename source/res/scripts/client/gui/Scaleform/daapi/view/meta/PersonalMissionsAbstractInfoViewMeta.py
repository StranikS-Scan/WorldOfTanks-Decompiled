# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionsAbstractInfoViewMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionsAbstractInfoViewMeta(View):

    def bigBtnClicked(self):
        self._printOverrideError('bigBtnClicked')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by PersonalMissionsAbstractInfoViewVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_updateS(self, data):
        """
        :param data: Represented by OperationAwardsVO (AS)
        """
        return self.flashObject.as_update(data) if self._isDAAPIInited() else None
