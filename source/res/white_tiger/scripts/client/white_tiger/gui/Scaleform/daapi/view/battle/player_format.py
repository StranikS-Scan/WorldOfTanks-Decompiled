# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/player_format.py
from gui.battle_control.arena_info.player_format import PlayerFullNameFormatter
from gui.impl import backport
from gui.impl.gen import R
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS

class WhiteTigerPlayerFullNameFormatter(PlayerFullNameFormatter):

    def format(self, vInfoVO, playerName=None):
        tags = vInfoVO.vehicleType.tags
        name = playerName
        if WT_VEHICLE_TAGS.MINIBOSS in tags:
            name = backport.text(R.strings.white_tiger_battle.botNames.Ermelinda())
        elif WT_VEHICLE_TAGS.BOT in tags:
            name = backport.text(R.strings.white_tiger_battle.playersPanel.botName())
        return super(WhiteTigerPlayerFullNameFormatter, self).format(vInfoVO, playerName=name)
