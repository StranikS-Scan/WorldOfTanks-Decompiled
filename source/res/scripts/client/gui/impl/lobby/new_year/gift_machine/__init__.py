# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_machine/__init__.py
import math
from helpers import time_utils

def getRentDaysLeftByExpiryTime(rentExpiryTime):
    currentTime = time_utils.getCurrentTimestamp()
    rentLeftTime = rentExpiryTime - currentTime if rentExpiryTime > currentTime else 0
    return int(math.ceil(rentLeftTime / time_utils.ONE_DAY))


def getVehicleRewardSpecialArg(reward, index, default=None):
    specialArgs = reward.get('specialArgs', [])
    argsLen = len(specialArgs)
    value = specialArgs[index] if index < argsLen else None
    return default if value is None else value
