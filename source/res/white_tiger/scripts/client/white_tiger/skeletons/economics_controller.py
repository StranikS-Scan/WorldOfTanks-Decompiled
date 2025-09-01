# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/skeletons/economics_controller.py
from skeletons.gui.game_control import IGameController, ISeasonProvider
from Event import Event
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterator
    from gui.server_events.bonuses import SimpleBonus

class IEconomicsController(IGameController, ISeasonProvider):
    onProgressUpdated = None
    onRewardsUpdated = None
    onProgressSeenByUser = None

    def getConfig(self):
        raise NotImplementedError

    def getStampsCountPerLevel(self):
        raise NotImplementedError

    def getProgressionMaxLevel(self):
        raise NotImplementedError

    def getStampsCount(self):
        raise NotImplementedError

    def getMaxRequiredStampsCount(self):
        raise NotImplementedError

    def getCurrentLevel(self):
        raise NotImplementedError

    def getTicketCount(self):
        raise NotImplementedError

    def getQuickTicketCount(self):
        raise NotImplementedError

    def getQuickBossTicketExpiryTime(self):
        raise NotImplementedError

    def getQuickHunterTicketCount(self):
        raise NotImplementedError

    def getQuickHunterTicketExpiryTime(self):
        raise NotImplementedError

    def getTicketTokenName(self):
        raise NotImplementedError

    def getStampTokenName(self):
        raise NotImplementedError

    def getQuickTicketTokenName(self):
        raise NotImplementedError

    def getQuickHunterTicketTokenName(self):
        raise NotImplementedError

    def hasEnoughTickets(self):
        raise NotImplementedError

    def getProgressionRewards(self):
        raise NotImplementedError

    def notifyProgressSeen(self):
        raise NotImplementedError
