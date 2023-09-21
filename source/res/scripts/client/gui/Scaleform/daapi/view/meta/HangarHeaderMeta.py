# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HangarHeaderMeta(BaseDAAPIComponent):

    def onQuestBtnClick(self, questType, questID):
        self._printOverrideError('onQuestBtnClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_createBattlePassS(self):
        return self.flashObject.as_createBattlePass() if self._isDAAPIInited() else None

    def as_removeBattlePassS(self):
        return self.flashObject.as_removeBattlePass() if self._isDAAPIInited() else None

    def as_createRankedBattlesS(self):
        return self.flashObject.as_createRankedBattles() if self._isDAAPIInited() else None

    def as_removeRankedBattlesS(self):
        return self.flashObject.as_removeRankedBattles() if self._isDAAPIInited() else None

    def as_createBattleRoyaleS(self):
        return self.flashObject.as_createBattleRoyale() if self._isDAAPIInited() else None

    def as_removeBattleRoyaleS(self):
        return self.flashObject.as_removeBattleRoyale() if self._isDAAPIInited() else None

    def as_createBattleRoyaleTournamentS(self):
        return self.flashObject.as_createBattleRoyaleTournament() if self._isDAAPIInited() else None

    def as_removeBattleRoyaleTournamentS(self):
        return self.flashObject.as_removeBattleRoyaleTournament() if self._isDAAPIInited() else None

    def as_createEpicWidgetS(self):
        return self.flashObject.as_createEpicWidget() if self._isDAAPIInited() else None

    def as_removeEpicWidgetS(self):
        return self.flashObject.as_removeEpicWidget() if self._isDAAPIInited() else None

    def as_createFunRandomWidgetS(self):
        return self.flashObject.as_createFunRandomWidget() if self._isDAAPIInited() else None

    def as_removeFunRandomWidgetS(self):
        return self.flashObject.as_removeFunRandomWidget() if self._isDAAPIInited() else None

    def as_setSecondaryEntryPointVisibleS(self, value):
        return self.flashObject.as_setSecondaryEntryPointVisible(value) if self._isDAAPIInited() else None

    def as_setResourceWellEntryPointS(self, value):
        return self.flashObject.as_setResourceWellEntryPoint(value) if self._isDAAPIInited() else None

    def as_setBattleMattersEntryPointS(self, value):
        return self.flashObject.as_setBattleMattersEntryPoint(value) if self._isDAAPIInited() else None

    def as_createComp7S(self):
        return self.flashObject.as_createComp7() if self._isDAAPIInited() else None

    def as_removeComp7S(self):
        return self.flashObject.as_removeComp7() if self._isDAAPIInited() else None

    def as_createEventWidgetS(self):
        return self.flashObject.as_createEventWidget() if self._isDAAPIInited() else None

    def as_removeEventWidgetS(self):
        return self.flashObject.as_removeEventWidget() if self._isDAAPIInited() else None
