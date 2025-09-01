# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/common/one_time_gift_common/one_time_gift_token.py
import typing
from collections import namedtuple
from items import vehicles
from one_time_gift_constants import RewardType, LAUNCH_ID
if typing.TYPE_CHECKING:
    from typing import Tuple
Token = namedtuple('Token', ('prefix', 'branch', 'giftSummary'))
PREFIX = 'one_time_gift_' + str(LAUNCH_ID)
FULL_BRANCH_BLOCKER = PREFIX + ':' + RewardType.FULL_BRANCH.value
NEWBIE_BRANCH_BLOCKER = PREFIX + ':' + RewardType.NEWBIE_BRANCH.value
COLLECTOR_REWARD_BLOCKER = PREFIX + ':' + RewardType.COLLECTOR_REWARD.value
ADDITIONAL_REWARD_BLOCKER = PREFIX + ':' + RewardType.ADDITIONAL_REWARD.value

def _getVehicleName(vehIntCD):
    return vehicles.getVehicleType(vehIntCD).name.split(':')[-1]


def generateBranchToken(rewardType, branch, isPlayerNewbie, giftSummary):
    return ':'.join([PREFIX,
     getBranchString(branch),
     giftSummary,
     rewardType.value,
     str(int(isPlayerNewbie))])


def isBranchToken(token, branch):
    return token.startswith(':'.join([PREFIX, getBranchString(branch)]))


def isOneTimeGiftToken(token):
    return token.startswith(PREFIX)


def getBranchString(branch):
    return '{},{}'.format(_getVehicleName(branch[0]), _getVehicleName(branch[-1]))
