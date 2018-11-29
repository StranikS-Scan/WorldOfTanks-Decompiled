# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/progress.py
import logging
import typing
import BigWorld
import quest_progress
from constants import QUEST_PROGRESS_STATE
from gui.Scaleform.genConsts.QUEST_PROGRESS_BASE import QUEST_PROGRESS_BASE
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.shared.formatters import text_styles
from helpers import i18n
from helpers.time_utils import ONE_MINUTE
from personal_missions_constants import CONTAINER, DISPLAY_TYPE, MULTIPLIER_TYPE, MULTIPLIER_SCOPE
from shared_utils import first
from gui.server_events.personal_progress import ORDERED_ICON_IDS
_logger = logging.getLogger(__name__)
PARAMS_KEYS = {'vehicleHealthFactor': BigWorld.wg_getNiceNumberFormat,
 'stunSeveralTargets': BigWorld.wg_getIntegralFormat,
 'distanceGreatOrEqual': BigWorld.wg_getIntegralFormat}
UI_HEADER_TYPES = {DISPLAY_TYPE.BIATHLON: QUEST_PROGRESS_BASE.HEADER_PROGRESS_TYPE_BIATHLON,
 DISPLAY_TYPE.LIMITED: QUEST_PROGRESS_BASE.HEADER_PROGRESS_TYPE_LIMITED,
 DISPLAY_TYPE.SERIES: QUEST_PROGRESS_BASE.HEADER_PROGRESS_TYPE_SERIES,
 DISPLAY_TYPE.COUNTER: QUEST_PROGRESS_BASE.HEADER_PROGRESS_TYPE_COUNTER,
 DISPLAY_TYPE.NONE: QUEST_PROGRESS_BASE.HEADER_PROGRESS_TYPE_NONE}

class ClientProgress(quest_progress.IProgress):
    __slots__ = ('_description', '_commonProgress', '_progressGetter', '__isLocked', '__isChanged')

    def __init__(self, commonProgress, description):
        self._description = description
        self._commonProgress = commonProgress
        self._progressGetter = None
        self.__isLocked = False
        self.__isChanged = False
        return

    def isChanged(self):
        return self._commonProgress.isChanged() or self.__isChanged

    def markAsVisited(self):
        self._commonProgress.markAsVisited()
        self.__isChanged = False

    def getProgressID(self):
        return self._commonProgress.getProgressID()

    def checkIsCompleted(self):
        return False

    def updateProgress(self, progress):
        self._commonProgress.updateProgress(progress)

    def getVisibleScope(self):
        return self._commonProgress.getVisibleScope()

    def isMain(self):
        return self._commonProgress.isMain()

    def setProgressGetter(self, progressGetter):
        self._progressGetter = progressGetter

    def getState(self):
        return self._commonProgress.getState()

    def setState(self, state):
        self._commonProgress.setState(state)

    def markAsCompleted(self):
        self._commonProgress.setState(QUEST_PROGRESS_STATE.COMPLETED)

    def getCurrent(self):
        return self._progressGetter.getCurrent(self._commonProgress)

    def hasProgressForReset(self):
        return self.getCurrent() > 0 and self.getState() != QUEST_PROGRESS_STATE.COMPLETED

    def getGoal(self):
        return self._progressGetter.getGoal(self._commonProgress)

    def getRest(self):
        return max(self.getGoal() - self.getCurrent(), 0)

    def getMultiplier(self):
        multiplierData = self._commonProgress.getParam('multiplier')
        return multiplierData

    @classmethod
    def getContainerType(cls):
        raise NotImplementedError

    def postProcess(self, cache):
        raise NotImplementedError

    def getDisplayType(self):
        return self._description.displayType

    def isInOrGroup(self):
        return self._description.isInOrGroup

    def getFormattedMultiplierValue(self, scope=MULTIPLIER_SCOPE.CARD):
        multiplier = self.getMultiplier()
        if multiplier:
            multiplierValue = first(multiplier['task'].values())
            descr = text_styles.main(i18n.makeString(PERSONAL_MISSIONS.getMultiplierDescr(multiplier['type'], scope), value=multiplierValue))
            if scope == MULTIPLIER_SCOPE.POST_BATTLE:
                multiplierScopeStyle = text_styles.neutral
            else:
                multiplierScopeStyle = text_styles.warning
            if multiplier['type'] == MULTIPLIER_TYPE.ATTEMPTS:
                return text_styles.concatStylesToSingleLine(multiplierScopeStyle(i18n.makeString(PERSONAL_MISSIONS.BONUS_MULTIPLIER_ATTEMPTS)), ' ', descr)
            if multiplier['type'] == MULTIPLIER_TYPE.PROGRESS:
                return text_styles.concatStylesToSingleLine(multiplierScopeStyle(i18n.makeString(PERSONAL_MISSIONS.BONUS_MULTIPLIER_PROGRESS, value=multiplierValue)), ' ', descr)

    def isCompleted(self):
        return self.getState() == QUEST_PROGRESS_STATE.COMPLETED

    def setLocked(self, isLocked):
        if self.__isLocked != isLocked:
            self.__isLocked = isLocked
            self.__isChanged = True

    def isLocked(self):
        return self.__isLocked

    def _getOrderType(self):
        return QUEST_PROGRESS_BASE.MAIN_ORDER_TYPE if self._commonProgress.isMain() else QUEST_PROGRESS_BASE.ADD_ORDER_TYPE


class HeaderProgress(ClientProgress):
    __slots__ = ClientProgress.__slots__ + ('__labelsGetter', '_scope')

    def __init__(self, commonProgress, description):
        super(HeaderProgress, self).__init__(commonProgress, description)
        self.__labelsGetter = None
        self._scope = None
        return

    def postProcess(self, cache):
        multiplierValue = self.getMultiplier()
        state = self.getState()
        for progress in cache.itervalues():
            if progress.isMain() == self.isMain() and progress.getContainerType() == CONTAINER.BODY:
                if multiplierValue:
                    progress.setHeaderMuliplier(multiplierValue)
                if state:
                    progress.setState(state)

    @classmethod
    def getContainerType(cls):
        return CONTAINER.HEADER

    def setLabelsGetter(self, labelsGetter):
        self.__labelsGetter = labelsGetter

    def setCurrentScope(self, scope):
        self._scope = scope

    def getHeaderData(self):
        return {'progressType': UI_HEADER_TYPES[self._description.displayType],
         'orderType': self._getOrderType(),
         'header': self.getHeaderLabel(),
         'valueTitle': self.getBottomLabel(),
         'value': self.getCurrent(),
         'goal': self.getGoal(),
         'scope': self._scope,
         'state': self.getState()}

    def getProgress(self):
        return self._commonProgress.getProgress()

    def getHeaderLabel(self):
        return self.__labelsGetter.getHeaderLabel(self)

    def getBottomLabel(self):
        return self.__labelsGetter.getBottomLabel(self)


class BiathlonProgress(HeaderProgress):

    def getHeaderData(self):
        data = super(BiathlonProgress, self).getHeaderData()
        data['progress'] = self._progressGetter.getBiathlonProgress(self._commonProgress)
        return data

    def getBattlesLimit(self):
        return self._commonProgress.getBattlesLimit()

    def hasProgressForReset(self):
        return len(self._commonProgress.getBattles()) > 0 and self.getState() != QUEST_PROGRESS_STATE.COMPLETED


class BodyProgress(ClientProgress):
    __slots__ = ClientProgress.__slots__ + ('__metricsWrapper', '__templateID', '_generalQuestID', '__timeLeft', '__limiter', '__headerMultiplier')
    COMMON_PROGRESS_IDS = ('win', 'alive')

    def __init__(self, commonProgress, description, templateID):
        super(BodyProgress, self).__init__(commonProgress, description)
        self.__metricsWrapper = _MetricsWrappers()
        self.__templateID = templateID
        self._generalQuestID = None
        self.__timeLeft = None
        self.__limiter = None
        self.__headerMultiplier = None
        return

    def acceptWrappersVisitors(self, wrappersVisitors):
        for wrappersVisitor in wrappersVisitors:
            if wrappersVisitor.isSuitableForProgress(self):
                for wrapper, isTopMetric in wrappersVisitor.getWrappers():
                    self.__metricsWrapper.addMetricWrapper(wrapper, isTopMetric)

    def setHeaderMuliplier(self, multiplier):
        self.__headerMultiplier = multiplier

    def getLimiter(self):
        return self.__limiter

    def postProcess(self, cache):
        limiterID = self._description.limiterID
        if limiterID:
            if limiterID in cache:
                self.__limiter = cache[limiterID]
                if not isinstance(self.__limiter, BodyProgress):
                    _logger.error('Wrong description for limiter with ID:%s, in progress:%s, in quest:%s', limiterID, self.getProgressID(), self._generalQuestID)
            else:
                _logger.error('Limiter with ID:%s, not found for progress:%s, in quest:%s', limiterID, self.getProgressID(), self._generalQuestID)

    @classmethod
    def getContainerType(cls):
        return CONTAINER.BODY

    def isChanged(self):
        isChanged = super(BodyProgress, self).isChanged()
        return isChanged or self.__limiter.isChanged() if self.__limiter else isChanged

    def markAsVisited(self):
        super(BodyProgress, self).markAsVisited()
        if self.__limiter:
            self.__limiter.markAsVisited()

    def addMetricWrapper(self, wrapper, isTopMetric):
        self.__metricsWrapper.addMetricWrapper(wrapper, isTopMetric)

    def setGeneralQuestID(self, generalQuestID):
        self._generalQuestID = generalQuestID

    def getFullData(self):
        return {'progressID': self.getProgressID(),
         'initData': self._getStaticData(),
         'progressData': self.getProgress()}

    def getProgress(self):
        return {'state': self.getState(),
         'goal': self.getGoal(),
         'current': self.getCurrent(),
         'metrics': self.__metricsWrapper.getMetrics(self),
         'isLocked': self.isLocked()}

    def getTemplateID(self):
        return self.__templateID

    def setTimeLeft(self, timeLeft):
        if self.__timeLeft != timeLeft:
            self.__timeLeft = timeLeft
            return True
        return False

    def getTimeLeft(self):
        return self.__timeLeft

    def getCountDown(self):
        return self._commonProgress.getCountDown()

    def getLocalizationValues(self):
        data = {'goal': BigWorld.wg_getNiceNumberFormat(self.getGoal())}
        if self.getCountDown():
            data['timeLimit'] = BigWorld.wg_getNiceNumberFormat(float(self.getCountDown()) / ONE_MINUTE)
        for param, formatter in PARAMS_KEYS.iteritems():
            value = self._commonProgress.getParam(param)
            if value:
                data.update({param: formatter(value)})

        return data

    def isCumulative(self):
        return self._commonProgress.isCumulative()

    def getDescription(self):
        if self.getProgressID() in self.COMMON_PROGRESS_IDS:
            description = self.__getCommonDescription()
        else:
            description = i18n.makeString(('#personal_missions_details:%s_description_%s' % (self._generalQuestID, self.getProgressID())), **self.getLocalizationValues())
        if self.__limiter:
            warningText = i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_LIMITER_LABEL)
            limiterDescription = i18n.makeString(('#personal_missions_details:%s_description_%s' % (self._generalQuestID, self.__limiter.getProgressID())), **self.__limiter.getLocalizationValues())
            description = '%s\n%s %s' % (description, text_styles.alert(warningText), limiterDescription)
        return description

    def _getStaticData(self):
        return {'title': self.getTitle(),
         'description': self.getDescription(),
         'iconID': self.getIconID(),
         'orderType': self._getOrderType(),
         'multiplier': self.getFormattedMultiplierValue(),
         'progressType': self.getProgressType(),
         'topMetricIndex': self.__metricsWrapper.getTopMetricIdx(),
         'isInOrGroup': self._description.isInOrGroup}

    def getTitle(self):
        return i18n.makeString('#personal_missions_details:quest_common_condition_title_%s' % self.getProgressID()) if self.getProgressID() in self.COMMON_PROGRESS_IDS else i18n.makeString('#personal_missions_details:%s_title_%s' % (self._generalQuestID, self.getProgressID()))

    def getIconID(self):
        return self._description.iconID

    def getPriority(self):
        key = self.getIconID()
        return ORDERED_ICON_IDS.index(key) if key in ORDERED_ICON_IDS else len(ORDERED_ICON_IDS)

    def getProgressType(self):
        return 'cumulative' if self._commonProgress.isCumulative() else 'regular'

    def getMultiplier(self):
        return super(BodyProgress, self).getMultiplier() or self.__headerMultiplier

    def __getCommonDescription(self):
        return i18n.makeString('#personal_missions_details:quest_common_condition_description_%s' % 'isNotSpotted') if self.getProgressID() == 'alive' and self._commonProgress.getParam('shouldBeUnspotted') else i18n.makeString('#personal_missions_details:quest_common_condition_description_%s' % self.getProgressID())


class AverageProgress(BodyProgress):
    __slots__ = BodyProgress.__slots__ + ('__counter',)

    def __init__(self, commonProgress, description, templateID):
        super(AverageProgress, self).__init__(commonProgress, description, templateID)
        self.__counter = None
        return

    def postProcess(self, cache):
        super(AverageProgress, self).postProcess(cache)
        counterID = self.getCounterID()
        if counterID in cache:
            self.__counter = cache[counterID]
        else:
            _logger.error('Counter with ID:%s, not found for progress:%s, in quest:%s', counterID, self.getProgressID(), self._generalQuestID)

    def getCounterID(self):
        return self._description.counterID

    def getCounter(self):
        return self.__counter

    def getCurrent(self):
        return self._progressGetter.getAverageValue(self._commonProgress, self.getCounter())

    def getGoal(self):
        return self._progressGetter.getAverageGoal(self._commonProgress, self.getCounter())


class VehicleTypesProgress(BodyProgress):

    def getDoneTargets(self):
        return self._commonProgress.getUniqueKeys()

    def getLocalizationValues(self):
        data = super(VehicleTypesProgress, self).getLocalizationValues()
        data.update(uniqueGoal=BigWorld.wg_getIntegralFormat(self._commonProgress.getUniqueGoal()))
        return data


class _MetricsWrappers(object):
    __slots__ = ('__topMetricIdx', '__wrappers')

    def __init__(self):
        self.__topMetricIdx = -1
        self.__wrappers = []

    def addMetricWrapper(self, wrapper, isTopMetric):
        self.__wrappers.append(wrapper)
        if isTopMetric:
            self.__topMetricIdx = self.__wrappers.index(wrapper)

    def getTopMetricIdx(self):
        return self.__topMetricIdx

    def getMetrics(self, progress):
        return [ wrapper(progress) for wrapper in self.__wrappers ]
