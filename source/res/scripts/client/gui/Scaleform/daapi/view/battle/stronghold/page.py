# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/stronghold/page.py
from gui.Scaleform.daapi.view.battle.classic import ClassicPage
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
from gui.Scaleform.daapi.view.battle.stronghold.manager import StrongholdMarkersManager
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
_STRONGHOLD_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, StrongholdMarkersManager, KillCamMarkersManager)

class StrongholdPage(ClassicPage):

    def __init__(self, components=None, external=_STRONGHOLD_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        super(StrongholdPage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__soundControl = None
        return
