# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/arena_info/arena_descrs.py
from gui.impl import backport
from gui.impl.gen import R
from fun_random.gui.battle_control.arena_info.arena_descrs import FunRandomArenaDescription
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin
from fall_tanks.gui.battle_control.fall_tanks_battle_constants import WinStatus

class FallTanksArenaDescription(FunRandomArenaDescription, FallTanksBattleMixin):

    def getWinString(self, isInBattle=True):
        return backport.text(R.strings.fall_tanks.arenaDescription.winText())

    def getTeamWinStatus(self, team, isAlly):
        playerInfo = self.getFallTanksPlayerVehicleInfo()
        return WinStatus.fromPlayerPosition(playerInfo.racePosition, playerInfo.isFinished)
