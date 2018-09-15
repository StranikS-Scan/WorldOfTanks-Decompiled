# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HalloweenBattleSelectorMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HalloweenBattleSelectorMeta(BaseDAAPIComponent):

    def playerSelectionMade(self, isPvE):
        self._printOverrideError('playerSelectionMade')

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_enableButtonsS(self):
        return self.flashObject.as_enableButtons() if self._isDAAPIInited() else None

    def as_disableButtonsS(self):
        return self.flashObject.as_disableButtons() if self._isDAAPIInited() else None

    def as_startWithPvES(self, val):
        return self.flashObject.as_startWithPvE(val) if self._isDAAPIInited() else None

    def as_currentStateIsPvES(self):
        return self.flashObject.as_currentStateIsPvE() if self._isDAAPIInited() else None

    def as_initBattleSelectorS(self, data):
        """
        :param data: Represented by SelectorWindowStaticDataVO (AS)
        """
        return self.flashObject.as_initBattleSelector(data) if self._isDAAPIInited() else None
