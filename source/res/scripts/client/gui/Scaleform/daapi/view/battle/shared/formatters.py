# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/formatters.py
import math

def normalizeHealth(health):
    return max(0.0, health)


def getHealthPercent(health, maxHealth):
    return float(normalizeHealth(health)) / maxHealth


def normalizeHealthPercent(health, maxHealth):
    return int(math.ceil(getHealthPercent(health, maxHealth) * 100))


def formatHealthProgress(health, maxHealth):
    return '%d/%d' % (normalizeHealth(health), maxHealth)
