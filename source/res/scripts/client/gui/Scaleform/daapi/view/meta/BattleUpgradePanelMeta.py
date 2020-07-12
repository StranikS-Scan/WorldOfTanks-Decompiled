# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleUpgradePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleUpgradePanelMeta(BaseDAAPIComponent):

    def onSelectItem(self, itemID):
        self._printOverrideError('onSelectItem')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_toggleAlertStateS(self, isVisible, alertText=None):
        return self.flashObject.as_toggleAlertState(isVisible, alertText) if self._isDAAPIInited() else None

    def as_setVisibleS(self, isVisible):
        return self.flashObject.as_setVisible(isVisible) if self._isDAAPIInited() else None

    def as_showSelectAnimS(self, idx):
        return self.flashObject.as_showSelectAnim(idx) if self._isDAAPIInited() else None

    def as_showNotificationAnimS(self):
        return self.flashObject.as_showNotificationAnim() if self._isDAAPIInited() else None

    def as_hideNotificationAnimS(self):
        return self.flashObject.as_hideNotificationAnim() if self._isDAAPIInited() else None
