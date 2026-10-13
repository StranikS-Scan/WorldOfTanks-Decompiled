# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/meta/PortalBattleLoadingMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading

class PortalBattleLoadingMeta(BattleLoading):

    def as_setTipsS(self, data):
        return self.flashObject.as_setTips(data) if self._isDAAPIInited() else None
