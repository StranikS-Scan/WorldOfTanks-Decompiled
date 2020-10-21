# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleQueueMeta.py
from gui.Scaleform.daapi.view.meta.BaseBattleQueueMeta import BaseBattleQueueMeta

class BattleQueueMeta(BaseBattleQueueMeta):

    def startClick(self):
        self._printOverrideError('startClick')

    def as_setTypeInfoS(self, data):
        return self.flashObject.as_setTypeInfo(data) if self._isDAAPIInited() else None

    def as_setPlayersS(self, text):
        return self.flashObject.as_setPlayers(text) if self._isDAAPIInited() else None

    def as_setDPS(self, dataProvider):
        return self.flashObject.as_setDP(dataProvider) if self._isDAAPIInited() else None

    def as_showStartS(self, vis):
        return self.flashObject.as_showStart(vis) if self._isDAAPIInited() else None
