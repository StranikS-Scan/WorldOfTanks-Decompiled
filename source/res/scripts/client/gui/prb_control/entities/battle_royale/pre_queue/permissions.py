# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from helpers import time_utils, dependency
from gui.ranked_battles.constants import PrimeTimeStatus
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyalePermissions(PreQueuePermissions):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def canCreateSquad(self):
        currentSeason = self.__battleRoyaleController.getCurrentSeason()
        status, _, _ = self.__battleRoyaleController.getPrimeTimeStatus()
        if status != PrimeTimeStatus.AVAILABLE:
            return False
        if currentSeason and super(BattleRoyalePermissions, self).canCreateSquad():
            if currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                return True
        return False
