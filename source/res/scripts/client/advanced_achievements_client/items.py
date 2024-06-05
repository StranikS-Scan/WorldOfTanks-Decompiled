# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/advanced_achievements_client/items.py
import typing
import sys
from achievements20.cache import UIConfigFields, getCache, IconPositions, IconSizeMap
from advanced_achievements_client.constants import AchievementType
from helpers.dependency import replace_none_kwargs
from skeletons.gui.shared import IItemsCache
from gui.server_events.bonuses import getNonQuestBonuses, splitAdvancedAchievementsBonuses
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import List, Dict, Optional
    from gui.server_events.bonuses import SimpleBonus

class _Progress(object):
    __slots__ = ('current', 'total')

    def __init__(self, current=0, total=0):
        self.current = current
        self.total = total

    def isCompleted(self):
        return self.current >= self.total > 0

    def getAsPercent(self):
        return 0.0 if self.total == 0 else float(self.current) / self.total * 100

    def __iter__(self):
        yield self.current
        yield self.total

    def __iadd__(self, other):
        curr, total = other
        self.current += curr
        self.total += total
        return self

    def __add__(self, other):
        return _Progress(self.current + other.current, self.total + other.total)

    def __lt__(self, other):
        selfProgress = 0.0
        otherProgress = 0.0
        if self.total:
            selfProgress = float(self.current) / self.total
        if other.total:
            otherProgress = float(other.current) / other.total
        return selfProgress < otherProgress or selfProgress == otherProgress and self.total < other.total

    def __eq__(self, other):
        return int(self.current) == int(other.current) and int(self.total) == int(other.total)

    def __repr__(self):
        return '{}: {} of {}'.format(self.__class__.__name__, self.current, self.total)


class _Rewards(object):
    __slots__ = ('__points', '__bonuses')

    def __init__(self, points, bonuses):
        self.__points = points
        self.__bonuses = bonuses

    def getPoints(self):
        return self.__points

    def getBonuses(self, split=False):
        bonuses = []
        for key, value in self.__bonuses.items():
            bonuses.extend(getNonQuestBonuses(key, value, ctx=None))

        if split:
            bonuses = splitAdvancedAchievementsBonuses(bonuses)
        return bonuses


class _BaseGuiAchievement(object):
    __slots__ = ('_staticData', '__dossierDescr')

    class _FieldNames(object):
        TYPE = UIConfigFields.TYPE.value
        KEY = UIConfigFields.STRING_KEY.value
        BACKGROUND = UIConfigFields.BACKGROUND.value
        THEME = UIConfigFields.THEME.value
        ICON_POSITION = UIConfigFields.ICON_POSITION.value
        ORDER = UIConfigFields.ORDER.value
        ICON_SIZE_MAP = UIConfigFields.ICON_SIZE_MAP.value
        VEHICLE = UIConfigFields.VEHICLE.value

    _TYPE = None
    _OWN_SCORE = 0

    def __init__(self, staticData, dossierDescr=None):
        self._staticData = staticData
        self.__dossierDescr = dossierDescr

    @property
    def isDeprecated(self):
        return self._staticData.deprecated

    def getID(self):
        return self._staticData.id

    def getCategory(self):
        return self._staticData.type

    def getType(self):
        return self._TYPE

    def getDisplayType(self):
        return AchievementType(self._staticData.UI[self._FieldNames.TYPE]) if self._FieldNames.TYPE in self._staticData.UI else self.getType()

    def getStringKey(self):
        return self._staticData.UI.get(self._FieldNames.KEY, '')

    def getTheme(self):
        return self._staticData.UI.get(self._FieldNames.THEME, '')

    def getBackground(self):
        return self._staticData.UI.get(self._FieldNames.BACKGROUND, '')

    def getOpenByUnlock(self):
        return self._staticData.openByUnlock

    def getIconPosition(self):
        return self._staticData.UI.get(self._FieldNames.ICON_POSITION, IconPositions.CENTER.value)

    def getIconSizeMap(self):
        return self._staticData.UI.get(self._FieldNames.ICON_SIZE_MAP, IconSizeMap.DEFAULT.value)

    def getVehicle(self):
        return self._staticData.UI.get(self._FieldNames.VEHICLE, None)

    def _getOrder(self):
        return self._staticData.UI.get(self._FieldNames.ORDER, None)

    def getInheritorsIterator(self, depth, isRoot=True):
        if depth > 0:
            for child in self.getChildsIterator():
                for inheritor in child.getInheritorsIterator(depth - 1, isRoot=False):
                    yield inheritor

        if not isRoot:
            yield self

    def getChildsIterator(self):
        raise NotImplementedError

    def getProgress(self):
        raise NotImplementedError

    def getOwnScore(self):
        achievedValue, _, _ = self._staticData.getCurrentDataFromDossier(self._getDossier())
        maxValue = 0
        currentValue = 0
        for stage in self._staticData.stages:
            if achievedValue >= stage.get('value'):
                currentValue += stage.get('points', 0)
            maxValue += stage.get('points', 0)

        return _Progress(currentValue, maxValue)

    def getScore(self, excludeList=None):
        return self.getOwnScore()

    def getTimeStamp(self):
        timeStamp = self._staticData.getCurrentDataFromDossier(self._getDossier())[-1]
        return 0 if not timeStamp else timeStamp

    def getRewards(self):
        stageID = self.getNextOrLastStageID()
        return _Rewards(0, {}) if stageID is None else _Rewards(self._staticData.getStagePointsByValue(stageID), self._staticData.getStageBonusByValue(stageID))

    @staticmethod
    def makeAchievement(achievementID, achievementCategory, dossierDescr=None):
        staticData = getCache().getAchievementByID(achievementCategory, achievementID)
        if staticData.conditions.get('requiredAchievementIDs'):
            return CumulativeAchievement(staticData, dossierDescr)
        return SteppedAchievement(staticData, dossierDescr) if len(staticData.stages) > 1 else RegularAchievement(staticData, dossierDescr)

    @replace_none_kwargs(itemsCache=IItemsCache)
    def _getDossier(self, itemsCache=None):
        if self.__dossierDescr is None:
            self.__dossierDescr = itemsCache.items.getAccountDossier().getDossierDescr()
        return self.__dossierDescr

    def getCurrentStageID(self):
        _, achievedStage, _ = self._staticData.getCurrentDataFromDossier(self._getDossier())
        return achievedStage

    def getNextOrLastStageID(self):
        achievedValue, achievedStage, _ = self._staticData.getCurrentDataFromDossier(self._getDossier())
        nextStage = self._staticData.getActiveStage(achievedValue, achievedStage)
        if nextStage is not None:
            return nextStage['id']
        else:
            return achievedStage if self._staticData.isAnyStageCompleted(achievedStage) else None

    def getFakeAchievementForStage(self, stageID):
        return self


class RegularAchievement(_BaseGuiAchievement):
    __slots__ = ()
    _TYPE = AchievementType.REGULAR

    def getChildsIterator(self):
        return iter([])

    def getProgress(self):
        achievedValue, achievedStage, _ = self._staticData.getCurrentDataFromDossier(self._getDossier())
        nextStage = self._staticData.getActiveStage(achievedValue, achievedStage)
        maxValue = nextStage['value'] if nextStage else achievedValue
        return _Progress(achievedValue, maxValue)

    def getConditionID(self):
        return self._staticData.conditions.get('vehicle')


class VirtualStepAchievement(RegularAchievement):
    __slots__ = ('__realProgress', '__stepData')
    _TYPE = AchievementType.STEPPED

    def __init__(self, staticData, realProgress, stepData):
        super(VirtualStepAchievement, self).__init__(staticData)
        self.__realProgress = realProgress
        self.__stepData = stepData

    def getProgress(self):
        currentValue = min(self.__realProgress.current, self.__stepData['value'])
        return _Progress(currentValue, self.__stepData['value'])

    def getOwnScore(self):
        achievedValue, _, _ = self._staticData.getCurrentDataFromDossier(self._getDossier())
        maxValue = 0
        currentValue = 0
        maxStageID = self.__stepData['id']
        for stage in self._staticData.stages:
            if stage['id'] > maxStageID:
                return _Progress(currentValue, maxValue)
            if achievedValue >= stage.get('value'):
                currentValue += stage.get('points', 0)
            maxValue += stage.get('points', 0)

        return _Progress(currentValue, maxValue)

    def getRewards(self):
        stageID = self.__stepData['id']
        return _Rewards(self._staticData.getStagePointsByValue(stageID), self._staticData.getStageBonusByValue(stageID))

    def getNextOrLastStageID(self):
        return self.__stepData['id']

    def getFakeAchievementForStage(self, _):
        raise SoftException('Cannot be called from {}'.format(self.__class__.__name__))


class SteppedAchievement(RegularAchievement):
    __slots__ = ()
    _TYPE = AchievementType.STEPPED

    def getChildsIterator(self):
        realProgress = super(SteppedAchievement, self).getProgress()
        for stepData in self._staticData.stages:
            yield VirtualStepAchievement(self._staticData, realProgress, stepData)

    def getFakeAchievementForStage(self, stageID):
        realProgress = super(SteppedAchievement, self).getProgress()
        return VirtualStepAchievement(self._staticData, realProgress, self._staticData.stages[stageID - 1])


class CumulativeAchievement(_BaseGuiAchievement):
    __slots__ = ()
    _TYPE = AchievementType.CUMULATIVE

    def getChildsIterator(self):
        for achievementID in self.__getChildIDs():
            yield self.makeAchievement(achievementID, self.getCategory(), self._getDossier())

    def getProgress(self):
        result = _Progress()
        for child in self.getChildsIterator():
            childProgress = child.getProgress()
            if child.getType() == AchievementType.CUMULATIVE:
                result += childProgress
            if childProgress.isCompleted():
                result.current += 1
            result.total += 1

        return result

    def getScore(self, excludeList=None):
        if excludeList is None:
            excludeList = []
        score = self.getOwnScore()
        for child in self.getChildsIterator():
            childId = child.getID()
            if childId not in excludeList:
                score += child.getScore(excludeList)
                excludeList.append(childId)

        return score

    def __getChildIDs(self):
        order = self._getOrder()
        requiredAchievementIDs = list(self._staticData.conditions.get('requiredAchievementIDs', set()))
        if order:
            requiredAchievementIDs.sort(key=lambda id: order.index(id) if id in order else sys.maxint)
        else:
            requiredAchievementIDs.sort()
        return requiredAchievementIDs


def createAchievement(achievementID, achievementCategory, dossierDescr=None):
    return _BaseGuiAchievement.makeAchievement(achievementID, achievementCategory, dossierDescr)
