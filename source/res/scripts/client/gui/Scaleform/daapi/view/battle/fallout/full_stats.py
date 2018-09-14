# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/full_stats.py
from gui.Scaleform.daapi.view.meta.FCStatsMeta import FCStatsMeta
from gui.Scaleform.daapi.view.meta.FMStatsMeta import FMStatsMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class FalloutClassicFullStats(FCStatsMeta):
    pass


class FalloutMultiTeamFullStats(FMStatsMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(FalloutMultiTeamFullStats, self)._populate()
        self.as_setSubTypeS(self.sessionProvider.getArenaDP().getMultiTeamsType())
