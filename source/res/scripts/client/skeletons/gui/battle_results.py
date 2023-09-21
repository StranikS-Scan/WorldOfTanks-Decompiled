# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/battle_results.py
from Event import Event

class IBattleResultsService(object):
    __slots__ = ()
    onResultPosted = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def requestResults(self, ctx, callback=None):
        raise NotImplementedError

    def requestEmblem(self, ctx, callback=None):
        raise NotImplementedError

    def postResult(self, result, needToShowUI=True):
        raise NotImplementedError

    def areResultsPosted(self, arenaUniqueID):
        raise NotImplementedError

    def getResultsVO(self, arenaUniqueID):
        raise NotImplementedError

    @property
    def presenter(self):
        raise NotImplementedError

    def popResultsAnimation(self, arenaUniqueID):
        raise NotImplementedError

    def saveStatsSorting(self, bonusType, iconType, sortDirection):
        raise NotImplementedError

    def applyAdditionalBonus(self, arenaUniqueID):
        raise NotImplementedError

    def isAddXPBonusApplied(self, arenaUniqueID):
        raise NotImplementedError

    def isAddXPBonusEnabled(self, arenaUniqueID):
        raise NotImplementedError

    def getAdditionalXPValue(self, arenaUniqueID):
        raise NotImplementedError

    def canApplyAdditionalXPBonus(self, arenaBonusType):
        raise NotImplementedError

    def isCrewSameForArena(self, arenaUniqueID):
        raise NotImplementedError

    def isXPToTManSameForArena(self, arenaUniqueID):
        raise NotImplementedError

    def getVehicleForArena(self, arenaUniqueID):
        raise NotImplementedError
