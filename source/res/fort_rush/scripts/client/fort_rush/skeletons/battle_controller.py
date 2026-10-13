# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/skeletons/battle_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from gui.prb_control.items import ValidationResult
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import List, Optional
    from Event import Event

class IFortRushBattleController(IGameController):
    onConfigUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isWithinActiveTimeframe(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isInAnnouncement(self):
        raise NotImplementedError

    def getTimeLeft(self):
        raise NotImplementedError

    def isEventPrbActive(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def selectBattle(self):
        raise NotImplementedError

    def selectRandomBattle(self):
        raise NotImplementedError

    def isInfoPageEnabled(self):
        raise NotImplementedError

    def getNewDailyMissionsTimestamp(self):
        raise NotImplementedError

    def getFortRushDailyQuests(self):
        raise NotImplementedError

    def getTotalProgressionPoints(self):
        raise NotImplementedError

    def getCurrentStageIndex(self):
        raise NotImplementedError

    def getCurrentStagePoints(self):
        raise NotImplementedError

    def isProgressionCompleted(self):
        raise NotImplementedError

    def getCurrentProgressionStageRewards(self):
        raise NotImplementedError

    def getProgressionRewards(self, questId):
        raise NotImplementedError

    def getEligibleVehicleTiers(self):
        raise NotImplementedError

    def getForbiddenVehClasses(self):
        raise NotImplementedError

    def isSuitableVehicle(self, vehicle):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def getLastStageThreshold(self):
        raise NotImplementedError
