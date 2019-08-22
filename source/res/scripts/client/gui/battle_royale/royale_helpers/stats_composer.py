# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_helpers/stats_composer.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BattleRoyaleStatsComposer(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, settings):
        super(BattleRoyaleStatsComposer, self).__init__()
        self.__settings = settings

    @property
    def battlesAmount(self):
        return self.__itemsCache.items.battleRoyale.battlesAmount

    @property
    def killsAmount(self):
        return self.__itemsCache.items.battleRoyale.killsAmount

    @property
    def top1Count(self):
        return self.top1SoloCount + self.top1SquadCount

    @property
    def top1SoloCount(self):
        return self.__itemsCache.items.battleRoyale.top1SoloAmount

    @property
    def top1SquadCount(self):
        return self.__itemsCache.items.battleRoyale.top1SquadAmount

    @property
    def maxKillsCount(self):
        return self.__itemsCache.items.battleRoyale.maxKillsCount

    def clear(self):
        self.__settings = None
        return
