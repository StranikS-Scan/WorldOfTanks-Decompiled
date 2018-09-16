# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_battle_loading.py
import WWISE
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading

class FootballBattleLoading(BattleLoading):

    def _populate(self):
        super(FootballBattleLoading, self)._populate()
        WWISE.WW_setState('STATE_ext_football_music', 'STATE_ext_football_music_loadingscreen')
