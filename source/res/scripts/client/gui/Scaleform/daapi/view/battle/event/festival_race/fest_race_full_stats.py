# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/fest_race_full_stats.py
from gui.Scaleform.daapi.view.meta.FestRaceFullStatsMeta import FestRaceFullStatsMeta
from gui.impl import backport
from gui.impl.gen import R

class FestRaceFullStats(FestRaceFullStatsMeta):

    def _populate(self):
        super(FestRaceFullStats, self)._populate()
        arenaInfo = {'mapName': backport.text(R.strings.festival.festival.loading.map()),
         'battleTypeLocaleStr': backport.text(R.strings.festival.festival.loading.gametype()),
         'winText': backport.text(R.strings.festival.festival.tab.victory_hint())}
        self.as_setArenaHeaderInfoS(arenaInfo)
