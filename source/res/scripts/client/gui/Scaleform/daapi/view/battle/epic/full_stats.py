# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/full_stats.py
from gui.Scaleform.daapi.view.meta.EpicFullStatsMeta import EpicFullStatsMeta
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import i18n

class EpicFullStatsComponent(EpicFullStatsMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(EpicFullStatsComponent, self)._populate()
        self.as_initializeTextS({'myLaneText': i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_MY_LANE),
         'allLanesText': i18n.makeString(EPIC_BATTLE.TAB_SCREEN_SHOW_ALL_LANES)})
