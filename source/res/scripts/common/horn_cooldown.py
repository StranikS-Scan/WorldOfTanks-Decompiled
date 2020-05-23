# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/horn_cooldown.py
import BigWorld
import ten_year_countdown_config

class HornCooldown(object):

    def __init__(self, powerOneHorn, speedRecovery, maxPowerHorn, banTime, minPower):
        self.__minPower = maxPowerHorn - minPower
        self.__maxPowerHorn = maxPowerHorn
        self.__powerOneHorn = powerOneHorn
        self.__speedRecovery = speedRecovery
        self.__powerHorn = maxPowerHorn
        self.__curPowerHorn = self.__powerHorn
        self.__lastTime = -1
        self.__banTime = banTime
        self.__needReduce = True

    def ask(self):
        if self.__lastTime > -1:
            curTime = BigWorld.time()
            diffTime = curTime - self.__lastTime
            if diffTime < self.__banTime:
                return False
            self.__lastTime = curTime
            self.__increase(diffTime)
        else:
            self.__lastTime = BigWorld.time()
        self.__curPowerHorn = self.__powerHorn
        if self.__powerHorn >= self.__minPower:
            self.__needReduce = True
        if self.__needReduce:
            self.__reduce()
        if self.__powerHorn == 0:
            self.__needReduce = False
        return True

    def getPowerHorn(self):
        power = self.__maxPowerHorn - self.__curPowerHorn
        return power if self.__needReduce else -power

    def getTimeRecoveryHorn(self):
        try:
            timeRecovery = int((self.__maxPowerHorn - self.__powerHorn) / self.__speedRecovery)
        except ZeroDivisionError:
            timeRecovery = 60

        return timeRecovery

    def __increase(self, diffTime):
        self.__powerHorn += int(round(diffTime * self.__speedRecovery))
        if self.__powerHorn > self.__maxPowerHorn:
            self.__powerHorn = self.__maxPowerHorn

    def __reduce(self):
        self.__powerHorn -= self.__powerOneHorn
        if self.__powerHorn < 0:
            self.__powerHorn = 0


def createHornCooldown():
    return HornCooldown(ten_year_countdown_config.HornParams.POWER_ONE_HORN, ten_year_countdown_config.HornParams.SPEED_RECOVERY, ten_year_countdown_config.HornParams.MAX_POWER, ten_year_countdown_config.HornParams.BAN_TIME, ten_year_countdown_config.HornParams.MIN_POWER)
