# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crystal_rewards_common.py
from constants import ARENA_BONUS_TYPE_NAMES
from soft_exception import SoftException

def readCrystalRewards(section, logId=''):
    results = {}
    for bonusTypeName, rewards in section.items():
        bonus_type = ARENA_BONUS_TYPE_NAMES.get(bonusTypeName)
        if not bonus_type:
            raise SoftException('%s %s: %s' % (section.name, logId, 'Unknown ARENA_BONUS_TYPE <%s>' % bonusTypeName))
        winner_rewards = rewards.readString('winner').strip()
        if not winner_rewards:
            raise SoftException('%s %s: %s' % (section.name, logId, 'not found <winner>'))
        loser_rewards = rewards.readString('loser').strip()
        if not loser_rewards:
            raise SoftException('%s %s: %s' % (section.name, logId, 'not found <loser>'))
        comparator = rewards.readString('comparator', 'fareTeamXPPosition')
        results[bonus_type] = {True: {i + 1:int(reward) for i, reward in enumerate(winner_rewards.split(' '))},
         False: {i + 1:int(reward) for i, reward in enumerate(loser_rewards.split(' '))},
         'comparator': comparator}

    return results
