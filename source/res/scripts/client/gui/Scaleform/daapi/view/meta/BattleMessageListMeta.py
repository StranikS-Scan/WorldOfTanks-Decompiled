# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleMessageListMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleMessageListMeta(BaseDAAPIComponent):

    def onRefreshComplete(self):
        self._printOverrideError('onRefreshComplete')

    def as_setupListS(self, data):
        return self.flashObject.as_setupList(data) if self._isDAAPIInited() else None

    def as_clearS(self):
        return self.flashObject.as_clear() if self._isDAAPIInited() else None

    def as_refreshS(self):
        return self.flashObject.as_refresh() if self._isDAAPIInited() else None

    def as_showYellowMessageS(self, key, text):
        return self.flashObject.as_showYellowMessage(key, text) if self._isDAAPIInited() else None

    def as_showRedMessageS(self, key, text):
        return self.flashObject.as_showRedMessage(key, text) if self._isDAAPIInited() else None

    def as_showPurpleMessageS(self, key, text):
        return self.flashObject.as_showPurpleMessage(key, text) if self._isDAAPIInited() else None

    def as_showGreenMessageS(self, key, text):
        return self.flashObject.as_showGreenMessage(key, text) if self._isDAAPIInited() else None

    def as_showGoldMessageS(self, key, text):
        return self.flashObject.as_showGoldMessage(key, text) if self._isDAAPIInited() else None

    def as_showSelfMessageS(self, key, text):
        return self.flashObject.as_showSelfMessage(key, text) if self._isDAAPIInited() else None
