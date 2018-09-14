# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/GasAttackSettings.py
import Math

class GasAttackState(object):
    NO = 0
    PREPARE = 1
    ATTACK = 2
    DONE = 3


class GasAttackSettings:
    DEATH_DELAY = 10

    def __init__(self, attackLength, preparationPeriod, position, startRadius, endRadius, compressionTime):
        self.attackLength = attackLength
        self.preparationPeriod = preparationPeriod
        self.position = Math.Vector3(position)
        self.startRadius = startRadius
        self.endRadius = endRadius
        self.compressionTime = compressionTime
        if compressionTime == 0:
            self.compressionSpeed = 0
            self.startRadius = self.endRadius
        else:
            self.compressionSpeed = float(startRadius - endRadius) / compressionTime


def gasAttackStateFor(settings, timeFromActivation):
    if timeFromActivation <= settings.preparationPeriod:
        return (GasAttackState.PREPARE, (settings.position, settings.startRadius))
    currentRadius = settings.startRadius - (timeFromActivation - settings.preparationPeriod) * settings.compressionSpeed
    return (GasAttackState.DONE, (settings.position, settings.endRadius)) if currentRadius <= settings.endRadius else (GasAttackState.ATTACK, (settings.position, currentRadius))
