# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/achievements20/WTRStageChecker.py
from bisect import bisect_right

class WTRStageChecker(object):
    __slots__ = ['_flatStages', '_stagesRatingsCache']

    def __init__(self, wtrStages):
        self._flatStages = [ (groupIndex + 1, stageIndex + 1, startRating) for groupIndex, group in enumerate(wtrStages) for stageIndex, startRating in enumerate(group) ]
        self._stagesRatingsCache = tuple((wtrStage[2] for wtrStage in self._flatStages))

    def getStage(self, wtr):
        index = bisect_right(self._stagesRatingsCache, wtr) - 1
        return None if index < 0 else self._flatStages[index]
