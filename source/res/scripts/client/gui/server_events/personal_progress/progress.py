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
from personal_missions_constants import CONTAINER, DISPLAY_TYPE
from shared_utils import first
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
    __slots__ = ('_description', '_commonProgress', '_progressGetter')

    def __init__(self, commonProgress, description):
        self._description = description
        self._commonProgress = commonProgress
        self._progressGetter = None
        return

    def isChanged(self):
        return self._commonProgress.isChanged()

    def markAsVisited(self):
        self._commonProgress.markAsVisited()

    def getProgressID(self):
        return self._commonProgress.getProgressID()

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

    def markAsCompleted(self):
        self._commonProgress.setState(QUEST_PROGRESS_STATE.COMPLETED)

    def getCurrent(self):
        return self._progressGetter.getCurrent(self._commonProgress)

    def getGoal(self):
        return self._progressGetter.getGoal(self._commonProgress)

    def getRest(self):
        return max(self.getGoal() - self.getCurrent(), 0)

    def getMultiplierValue(self):
        multiplierData = self._commonProgress.getParam('multiplier')
        return first(multiplierData.values()) if multiplierData else None

    @classmethod
    def getContainerType(cls):
        raise NotImplementedError

    def postProcess(self, cache):
        raise NotImplementedError

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
        multiplierValue = self.getMultiplierValue()
        if multiplierValue:
            for progress in cache.itervalues():
                if progress.isMain() == self.isMain() and progress.getContainerType() == CONTAINER.BODY:
                    progress.setHeaderMuliplier(multiplierValue)

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


class BodyProgress(ClientProgress):
    __slots__ = ClientProgress.__slots__ + ('__metricsWrapper', '__templateID', '_generalQuestID', '__timeLeft', '__limiter', '__headerMultiplierValue')

    def __init__(self, commonProgress, description, templateID):
        super(BodyProgress, self).__init__(commonProgress, description)
        self.__metricsWrapper = _MetricsWrappers()
        self.__templateID = templateID
        self._generalQuestID = None
        self.__timeLeft = None
        self.__limiter = None
        self.__headerMultiplierValue = None
        return

    def acceptWrappersVisitors(self, wrappersVisitors):
        for wrappersVisitor in wrappersVisitors:
            if wrappersVisitor.isSuitableForProgress(self):
                for wrapper, isTopMetric in wrappersVisitor.getWrappers():
                    self.__metricsWrapper.addMetricWrapper(wrapper, isTopMetric)

    def setHeaderMuliplier(self, multiplierValue):
        self.__headerMultiplierValue = multiplierValue

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
         'metrics': self.__metricsWrapper.getMetrics(self)}

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
        description = i18n.makeString(('#personal_missions_2_details:%s_description_%s' % (self._generalQuestID, self.getProgressID())), **self.getLocalizationValues())
        if self.__limiter:
            warningText = i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_LIMITER_LABEL)
            limiterDescription = i18n.makeString(('#personal_missions_2_details:%s_description_%s' % (self._generalQuestID, self.__limiter.getProgressID())), **self.__limiter.getLocalizationValues())
            description = '%s\n%s %s' % (description, text_styles.alert(warningText), limiterDescription)
        return description

    def _getStaticData(self):
        return {'title': self.getTitle(),
         'description': self.getDescription(),
         'iconID': self.getIconID(),
         'orderType': self._getOrderType(),
         'multiplier': self.__getMultiplier(),
         'progressType': self.getProgressType(),
         'topMetricIndex': self.__metricsWrapper.getTopMetricIdx(),
         'isInOrGroup': self._description.isInOrGroup}

    def getTitle(self):
        return i18n.makeString('#personal_missions_2_details:%s_title_%s' % (self._generalQuestID, self.getProgressID()))

    def getIconID(self):
        return self._description.iconID

    def getProgressType(self):
        return 'cumulative' if self._commonProgress.isCumulative() else 'regular'

    def getMultiplierValue(self):
        return super(BodyProgress, self).getMultiplierValue() or self.__headerMultiplierValue

    def __getMultiplier(self):
        multiplierValue = self.getMultiplierValue()
        if multiplierValue:
            multiplierStr = text_styles.neutral(i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_MULTIPLIER, value=multiplierValue))
            return '%s %s' % (multiplierStr, i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_MULTIPLIER_DESCRIPTION, value=multiplierValue))


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
        current = super(AverageProgress, self).getCurrent()
        return current / self.getCounter().getGoal()

    def getGoal(self):
        goal = super(AverageProgress, self).getGoal()
        return goal / self.getCounter().getGoal()


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
