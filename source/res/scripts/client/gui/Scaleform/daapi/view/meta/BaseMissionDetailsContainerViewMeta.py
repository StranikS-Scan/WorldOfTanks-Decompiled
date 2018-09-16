# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseMissionDetailsContainerViewMeta.py
from gui.Scaleform.framework.entities.View import View

class BaseMissionDetailsContainerViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def requestMissionData(self, index):
        self._printOverrideError('requestMissionData')

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setMissionDataS(self, data):
        return self.flashObject.as_setMissionData(data) if self._isDAAPIInited() else None
