# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/state_machine/state_helpers.py
import typing
from helpers import dependency
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
from one_time_gift_common.one_time_gift_constants import BranchListType

@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def canReceiveRewards(_, otgCtrl=None):
    return otgCtrl.isEntryPointEnabled


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def isNewbie(otgCtrl=None):
    return otgCtrl.isPlayerNewbie()


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def isCollectorsCompensationReceived(_=None, otgCtrl=None):
    return otgCtrl.isCollectorsCompensationReceived()


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def isFullListBranchReceived(_=None, otgCtrl=None):
    return otgCtrl.isFullListBranchReceived()


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def isNewbieBranchReceived(otgCtrl=None):
    return otgCtrl.isNewbieBranchReceived()


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def areAdditionalRewardsAvailable(_, otgCtrl=None):
    return not otgCtrl.isAdditionalRewardReceived()


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def isNewbieListPurchased(_, otgCtrl=None):
    return otgCtrl.isBranchListPurchased(BranchListType.NEWBIE)


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def isFullListPurchased(_, otgCtrl=None):
    return otgCtrl.isBranchListPurchased(BranchListType.ALL)


@dependency.replace_none_kwargs(otgCtrl=IOneTimeGiftController)
def getAvailabilityError(_=None, otgCtrl=None):
    return otgCtrl.getAvailabilityError()
