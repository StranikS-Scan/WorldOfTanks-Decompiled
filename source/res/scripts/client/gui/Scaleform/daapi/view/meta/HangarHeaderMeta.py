# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HangarHeaderMeta(BaseDAAPIComponent):

    def onQuestBtnClick(self, questType, questID):
        self._printOverrideError('onQuestBtnClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setSecondaryEntryPointVisibleS(self, value):
        return self.flashObject.as_setSecondaryEntryPointVisible(value) if self._isDAAPIInited() else None

    def as_addEntryPointS(self, alias):
        return self.flashObject.as_addEntryPoint(alias) if self._isDAAPIInited() else None

    def as_addSecondaryEntryPointS(self, alias, isRight):
        return self.flashObject.as_addSecondaryEntryPoint(alias, isRight) if self._isDAAPIInited() else None

    def as_setCollectiveGoalEntryPointS(self, value):
        return self.flashObject.as_setCollectiveGoalEntryPoint(value) if self._isDAAPIInited() else None

    def as_setArmoryYardEntryPointS(self, value):
        return self.flashObject.as_setArmoryYardEntryPoint(value) if self._isDAAPIInited() else None
