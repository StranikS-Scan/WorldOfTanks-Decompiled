# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RacesBattleLoadingMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading

class RacesBattleLoadingMeta(BattleLoading):

    def as_setTipsS(self, data):
        return self.flashObject.as_setTips(data) if self._isDAAPIInited() else None
