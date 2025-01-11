# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalMissionOperationsMeta.py
from gui.Scaleform.framework.entities.View import View

class PersonalMissionOperationsMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onTabSelected(self, tabIdx):
        self._printOverrideError('onTabSelected')

    def as_setSelectedTabS(self, tabIdx):
        return self.flashObject.as_setSelectedTab(tabIdx) if self._isDAAPIInited() else None
