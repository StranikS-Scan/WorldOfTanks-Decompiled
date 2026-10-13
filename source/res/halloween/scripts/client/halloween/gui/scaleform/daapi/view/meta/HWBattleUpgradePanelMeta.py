# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/HWBattleUpgradePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HWBattleUpgradePanelMeta(BaseDAAPIComponent):

    def onSelectItem(self, itemID):
        self._printOverrideError('onSelectItem')

    def onAppear(self):
        self._printOverrideError('onAppear')

    def onItemHover(self):
        self._printOverrideError('onItemHover')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setAnomaliesMatrixHotkeyS(self, hotKey):
        return self.flashObject.as_setAnomaliesMatrixHotkey(hotKey) if self._isDAAPIInited() else None

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
