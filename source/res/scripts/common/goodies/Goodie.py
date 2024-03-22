# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/Goodie.py
import time
from itertools import chain
from typing import Dict, Tuple
from debug_utils import LOG_DEBUG_DEV
from goodie_constants import GOODIE_STATE

def decrementExpirationsInOrder(amountToRemove, oldExpirations):
    updatedDict = oldExpirations.copy()
    orderedTimestamps = sorted(oldExpirations.iterkeys())
    for timestamp in orderedTimestamps:
        count = updatedDict[timestamp]
        if count > amountToRemove:
            updatedDict[timestamp] -= amountToRemove
            break
        amountToRemove -= count
        del updatedDict[timestamp]

    return updatedDict


def mergeExpirationsInto(source, target):
    for key in set(chain(source.iterkeys(), target.iterkeys())):
        value2 = target.get(key, 0)
        value1 = source.get(key, 0)
        target[key] = value1 + value2


class Goodie(object):
    __slots__ = ['uid',
     'state',
     'finishTime',
     'counter',
     'expirations']

    def __init__(self, uid, state=GOODIE_STATE.INACTIVE, finishTime=0, counter=0, expirations=None):
        self.uid = uid
        self.state = state
        self.finishTime = finishTime
        self.counter = counter
        self.expirations = {}
        if expirations is not None:
            self.expirations = expirations
        LOG_DEBUG_DEV('[GOODIE_EXPIRE] Goodie created: {}'.format(self))
        return

    def __repr__(self):
        return 'Goodie[{}, {}, {}, {}, {}]'.format(self.uid, self.state, self.finishTime, self.counter, self.expirations)

    def isActive(self):
        return self.state == GOODIE_STATE.ACTIVE

    def isEffectFinished(self):
        if self.finishTime and self.finishTime < time.time():
            return True
        else:
            return False

    def isExpirable(self):
        return bool(self.expirations)

    def isExpired(self):
        now = int(time.time())
        for expireTimeStamp in self.expirations:
            if expireTimeStamp <= now:
                return True

        return False

    def splitExpirations(self):
        expired = {}
        valid = {}
        now = int(time.time())
        for expireTimeStamp, count in self.expirations.iteritems():
            if expireTimeStamp <= now:
                expired[expireTimeStamp] = count
            valid[expireTimeStamp] = count

        return (expired, valid)

    def toPdata(self):
        return (self.state,
         self.finishTime,
         self.counter,
         self.expirations)
