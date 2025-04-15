# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineBattlePageMeta.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class FrontlineBattlePageMeta(ClassicPage):

    def onDeactivateRadialMenu(self):
        self._printOverrideError('onDeactivateRadialMenu')

    def as_setSelectReservesAvailableS(self, value):
        return self.flashObject.as_setSelectReservesAvailable(value) if self._isDAAPIInited() else None

    def as_setVehPostProgressionEnabledS(self, value):
        return self.flashObject.as_setVehPostProgressionEnabled(value) if self._isDAAPIInited() else None
