# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/formatters.py
import math
from debug_utils import LOG_ERROR

def normalizeHealth(health):
    return max(0.0, health)


def getHealthPercent(health, maxHealth):
    if not (maxHealth > 0 and maxHealth >= health):
        LOG_ERROR('Maximum health is not valid! health={}, maxHealth={}'.format(health, maxHealth))
        return 0.0
    return float(normalizeHealth(health)) / maxHealth


def normalizeHealthPercent(health, maxHealth):
    return int(math.ceil(getHealthPercent(health, maxHealth) * 100))


def formatHealthProgress(health, maxHealth):
    if not (maxHealth > 0 and maxHealth >= health):
        LOG_ERROR('Maximum health is not valid! health={}, maxHealth={}'.format(health, maxHealth))
    return '%d/%d' % (normalizeHealth(health), maxHealth)
