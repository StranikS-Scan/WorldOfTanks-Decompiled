# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/skeletons/gui/game_control.py
import typing
from one_time_gift.helpers.server_settings import OneTimeGiftConfig
from skeletons.gui.game_control import IGameController
from one_time_gift_common.one_time_gift_constants import BranchListType, TechTreeBranch
if typing.TYPE_CHECKING:
    from typing import Callable, Optional
    T_PROCESSOR_CALLBACK = Callable[[bool], None]

class IOneTimeGiftController(IGameController):
    onSettingsChanged = None
    onEntryPointUpdated = None
    onPlayerOTGStatusChanged = None

    @property
    def isEntryPointEnabled(self):
        raise NotImplementedError

    @property
    def isEntryPointShown(self):
        raise NotImplementedError

    def markEntryPointShown(self):
        raise NotImplementedError

    def areAllRewardsReceived(self, *_):
        raise NotImplementedError

    def getAvailabilityError(self):
        raise NotImplementedError

    def getBranchById(self, branchId, fromList):
        raise NotImplementedError

    def getBranchesSortedForNation(self, fromList):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getEndTime(self):
        raise NotImplementedError

    def getStartTime(self):
        raise NotImplementedError

    def getRemindTime(self):
        raise NotImplementedError

    def getRemindBattlesAmount(self):
        raise NotImplementedError

    def isAdditionalRewardReceived(self):
        raise NotImplementedError

    def isBranchListPurchased(self, branchListType):
        raise NotImplementedError

    def isCollectorsCompensationReceived(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isFullListBranchReceived(self):
        raise NotImplementedError

    def isNewbieBranchReceived(self):
        raise NotImplementedError

    def isPlayerNewbie(self):
        raise NotImplementedError

    def onEntryPointClicked(self):
        raise NotImplementedError

    def onShowInfoClicked(self, ctx=None):
        raise NotImplementedError

    def onViewError(self):
        raise NotImplementedError
