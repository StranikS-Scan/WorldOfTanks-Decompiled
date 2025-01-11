# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bob/page.py
from gui.Scaleform.daapi.view.battle.bob.marker_manager import BobMarkersManager
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared import crosshair
_EXTERNAL_COMPONENTS = (crosshair.CrosshairPanelContainer, BobMarkersManager)

class BobPage(ClassicPage):

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        self._fullStatsAlias = fullStatsAlias
        super(BobPage, self).__init__(components=components, external=external)
