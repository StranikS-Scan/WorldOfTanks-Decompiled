# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreActionsViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreActionsViewMeta(BaseDAAPIComponent):

    def actionSelect(self, triggerChainID):
        self._printOverrideError('actionSelect')

    def onBattleTaskSelect(self, actionId):
        self._printOverrideError('onBattleTaskSelect')

    def onActionSeen(self, actionId):
        self._printOverrideError('onActionSeen')

    def as_setDataS(self, storeActionsData):
        return self.flashObject.as_setData(storeActionsData) if self._isDAAPIInited() else None

    def as_actionTimeUpdateS(self, actionsTime):
        return self.flashObject.as_actionTimeUpdate(actionsTime) if self._isDAAPIInited() else None
