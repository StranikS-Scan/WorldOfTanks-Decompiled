# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/common/one_time_gift_common/one_time_gift_constants.py
from collections import namedtuple
from enum import Enum
OTG_BRANCHES_CONFIG_PATH = 'one_time_gift/scripts/item_defs/vehicles/common/one_time_gift_branches.xml'
OTG_GAME_PARAMS_KEY = 'one_time_gift_config'
MIN_OTG_VEH_LEVEL = 6
MAX_OTG_VEH_LEVEL = 10
EVENT_NAME = 'one_time_gift_event'
LAUNCH_ID = 202509
TechTreeBranch = namedtuple('TechTreeBranch', ['branchId', 'vehCDs'])

class OTG_ERROR_CODES(object):
    NOT_AVAILABLE = 'NOT_AVAILABLE'
    DISABLED = 'DISABLED'
    NOT_ACTIVE = 'NOT_ACTIVE'
    REWARD_RECEIVED = 'REWARD_RECEIVED'
    WRONG_ARGS = 'WRONG_ARGS'
    NOT_OWNED = 'NOT_OWNED'
    RENTED = 'RENTED'


class OTG_OP_TYPES(object):
    RESEARCH = 200
    ACCRUAL = 201
    RENT_REMOVAL = 202


class RewardType(Enum):
    FULL_BRANCH = 'full_list_branch'
    NEWBIE_BRANCH = 'newbie_list_branch'
    COLLECTOR_REWARD = 'collector_compensation'
    ADDITIONAL_REWARD = 'additional_reward'


class BranchListType(Enum):
    NEWBIE = 'newbie'
    ALL = 'allPlayers'


BRANCH_BY_REWARD = {RewardType.NEWBIE_BRANCH: BranchListType.NEWBIE.value,
 RewardType.FULL_BRANCH: BranchListType.ALL.value}
BRANCHES = set([ status.value for status in BranchListType ])
