# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/zombie_settings.py
from debug_utils import LOG_DEBUG_DEV

class ZombieSettings(object):

    def __init__(self):
        LOG_DEBUG_DEV('ZombieSettings')
        self.zombieRadius = 1
        self.zombieSleepRadius = 1
        self.zombieSleepDelay = 0

    def setZombieRadius(self, radius):
        LOG_DEBUG_DEV('[ZOMBIE_SETTINGS] Zombie Radius: ', radius)
        self.zombieRadius = radius

    def setZombieSleepRadius(self, radius):
        LOG_DEBUG_DEV('[ZOMBIE_SETTINGS] Zombie Sleep Radius: ', radius)
        self.zombieSleepRadius = radius

    def setZombieSleepDelay(self, delay):
        LOG_DEBUG_DEV('[ZOMBIE_SETTINGS] Zombie Sleep Delay: ', delay)
        self.zombieSleepDelay = delay
