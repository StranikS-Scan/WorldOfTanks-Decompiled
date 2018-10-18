# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HangarHeaderMeta(BaseDAAPIComponent):

    def onQuestBtnClick(self, questType, questID):
        self._printOverrideError('onQuestBtnClick')

    def onProgressClicked(self):
        self._printOverrideError('onProgressClicked')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setBonusDataS(self, data):
        return self.flashObject.as_setBonusData(data) if self._isDAAPIInited() else None

    def as_setBonusVisibleS(self, value):
        return self.flashObject.as_setBonusVisible(value) if self._isDAAPIInited() else None
