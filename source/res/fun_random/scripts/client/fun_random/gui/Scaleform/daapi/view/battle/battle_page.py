# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/battle_page.py
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from fun_random.gui.Scaleform.daapi.view.battle.markers2d import FunRandomMarkersManager

class FunRandomBattlePage(ClassicPage):

    def __init__(self, components=None, external=(CrosshairPanelContainer, FunRandomMarkersManager), fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        super(FunRandomBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
