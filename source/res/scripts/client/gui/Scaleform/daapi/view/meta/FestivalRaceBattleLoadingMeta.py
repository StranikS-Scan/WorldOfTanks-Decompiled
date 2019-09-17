# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestivalRaceBattleLoadingMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading

class FestivalRaceBattleLoadingMeta(BattleLoading):

    def as_setHintS(self, title, message):
        return self.flashObject.as_setHint(title, message) if self._isDAAPIInited() else None

    def as_setAddIconS(self, iconPath):
        return self.flashObject.as_setAddIcon(iconPath) if self._isDAAPIInited() else None
