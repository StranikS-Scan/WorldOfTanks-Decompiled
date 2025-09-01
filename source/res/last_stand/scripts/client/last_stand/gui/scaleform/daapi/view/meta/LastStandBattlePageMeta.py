# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/LastStandBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class LastStandBattlePageMeta(ClassicPage):

    def as_updateDamageScreenS(self, isVisible):
        return self.flashObject.as_updateDamageScreen(isVisible) if self._isDAAPIInited() else None
