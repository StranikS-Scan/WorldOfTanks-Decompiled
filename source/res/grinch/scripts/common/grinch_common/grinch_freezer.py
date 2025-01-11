# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/grinch_freezer.py
from collections import namedtuple
EXPIRABLE_FREEZER_COMPONENT_NAME = 'freezer_expirable'
FREEZER_COMPONENT_NAME = 'freezer'
FREEZER_DEBUF_COMPONENT_NAME = 'freezer_debuff'
FREEZER_LOCK_ABILITIES_COMPONENT_NAME = 'freezer_lock_abilities'
FREEZER_KILL_TRACKER_COMPONENT_NAME = 'freezer_kill_tracker'
FREEZER_DAMAGE_TRACKER_COMPONENT_NAME = 'freezer_damage_tracker'
ROCKET_ACCELERATION_DISABLER = 'rocketAccelerationDisabler'
_FreezingConfig = namedtuple('_FreezingConfig', ('freezingTime', 'freezeDuration', 'freezeDamage', 'debuffFactors', 'team'))

class _AttackersData(object):
    __slots__ = ('__attackers', '__data')

    def __init__(self, attackerId, data):
        super(_AttackersData, self).__init__()
        self.__attackers = [attackerId]
        self.__data = {attackerId: data}

    def getCurrentAttacker(self):
        if self.__attackers:
            attackerId = self.__attackers[-1]
            return (attackerId, self.__data[attackerId])
        else:
            return (-1, None)

    def addAttacker(self, attackerId, data):
        if attackerId not in self.__data:
            self.__data[attackerId] = data
            self.__attackers.append(attackerId)

    def removeAttacker(self, attackerId):
        if attackerId in self.__data:
            self.__attackers.remove(attackerId)
            del self.__data[attackerId]

    def iterAttackersData(self):
        for attackerId in self.__attackers:
            yield self.__data[attackerId]

    def iterAttackers(self):
        for attackerId in self.__attackers:
            yield (attackerId, self.__data[attackerId])

    def hasAttackers(self):
        return len(self.__attackers) > 0


class IAttacked(object):

    def getCurrentAttacker(self):
        return None

    def addAttacker(self, attackerId, data):
        pass

    def removeAttacker(self, attackerId):
        pass

    def iterAttackersData(self):
        pass

    def iterAttackers(self):
        pass

    def getAttackersData(self):
        return None

    def hasAttackers(self):
        return False
