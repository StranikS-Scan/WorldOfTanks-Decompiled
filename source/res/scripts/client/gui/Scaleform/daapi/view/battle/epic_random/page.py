# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/page.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage, COMMON_CLASSIC_CONFIG, EXTENDED_CLASSIC_CONFIG
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
_EPIC_RANDOM_CLASSICS_COMPONENTS = COMMON_CLASSIC_CONFIG
_EPIC_RANDOM_EXTENDED_COMPONENTS = EXTENDED_CLASSIC_CONFIG

class EpicRandomPage(ClassicPage):

    def __init__(self, components=None, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        if components is None:
            components = _EPIC_RANDOM_CLASSICS_COMPONENTS if self.sessionProvider.isReplayPlaying else _EPIC_RANDOM_EXTENDED_COMPONENTS
        super(EpicRandomPage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        return

    def _onBattleLoadingStart(self):
        super(EpicRandomPage, self)._onBattleLoadingStart()
        if not self.sessionProvider.isReplayPlaying:
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING)

    def _onBattleLoadingFinish(self):
        super(EpicRandomPage, self)._onBattleLoadingFinish()
        if not self.sessionProvider.isReplayPlaying:
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
