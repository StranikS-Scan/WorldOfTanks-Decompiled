# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/page.py
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

class BobPage(ClassicPage):

    def __init__(self, components=None, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        self._fullStatsAlias = fullStatsAlias
        super(BobPage, self).__init__(components=components, external=external)
