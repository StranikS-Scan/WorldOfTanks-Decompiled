# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BuffonRecruitmentMeta.py
from gui.Scaleform.framework.entities.View import View

class BuffonRecruitmentMeta(View):

    def onCloseView(self):
        self._printOverrideError('onCloseView')

    def onApply(self, data):
        self._printOverrideError('onApply')

    def as_initDataS(self, data):
        return self.flashObject.as_initData(data) if self._isDAAPIInited() else None

    def as_updateRankS(self, rankStr):
        return self.flashObject.as_updateRank(rankStr) if self._isDAAPIInited() else None
