# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/formatters.py
from collections import namedtuple
from constants import QUEST_PROGRESS_STATE
from gui.Scaleform.genConsts.QUEST_PROGRESS_BASE import QUEST_PROGRESS_BASE
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.server_events.personal_progress.storage import PostBattleProgressStorage, LobbyProgressStorage
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
from personal_missions_constants import DISPLAY_TYPE, MULTIPLIER_SCOPE
from shared_utils import first, findFirst

class ProgressesFormatter(object):
    __slots__ = ('_storage', '_dummyHeaderType')

    def __init__(self, storage, dummyHeaderType=DISPLAY_TYPE.SIMPLE):
        self._storage = storage
        self._dummyHeaderType = dummyHeaderType

    def bodyFormat(self, isMain=None):
        result = []
        if self._storage:
            progresses = self._storage.getBodyProgresses(isMain)
            if progresses:
                sortedProgresses = self._sortedBodyProgresses(progresses)
                for progress in sortedProgresses:
                    result.append(self._makeBodyProgressData(progress))

        return result

    def headerFormat(self, isMain=None):
        result = []
        if self._storage:
            if isMain is not None:
                progresses = self._storage.getHeaderProgresses(isMain)
                if progresses:
                    result.append(first(progresses.values()).getHeaderData())
                else:
                    result.append(self.__addDummyHeaderProgress(isMain))
            else:
                progresses = self._storage.getHeaderProgresses()
                mainProgresses, addProgresses = [], []
                for progress in progresses.itervalues():
                    if progress.isMain():
                        mainProgresses.append(progress)
                    addProgresses.append(progress)

                if mainProgresses:
                    result.append(first(mainProgresses).getHeaderData())
                else:
                    result.append(self.__addDummyHeaderProgress(isMain=True))
                if addProgresses:
                    result.append(first(addProgresses).getHeaderData())
                else:
                    result.append(self.__addDummyHeaderProgress(isMain=False))
        return result

    @classmethod
    def _makeBodyProgressData(cls, progress):
        return progress.getFullData()

    @classmethod
    def _sortedBodyProgresses(cls, progresses):
        return sorted(progresses.itervalues(), key=lambda p: (not p.isMain(), p.getPriority()))

    def __addDummyHeaderProgress(self, isMain):
        orderType = QUEST_PROGRESS_BASE.ADD_ORDER_TYPE
        key = PERSONAL_MISSIONS.CONDITIONS_UNLIMITED_LABEL_ADD
        if isMain:
            orderType = QUEST_PROGRESS_BASE.MAIN_ORDER_TYPE
            key = PERSONAL_MISSIONS.CONDITIONS_UNLIMITED_LABEL_MAIN
        return {'progressType': self._dummyHeaderType,
         'orderType': orderType,
         'header': i18n.makeString(key)}


def _packCondition(title, strConditions):
    return '%s\n%s' % (text_styles.leadingText(text_styles.middleTitle(title), 1), text_styles.main(strConditions))


def _areMainConditionsCompleted(mainProgresses):
    return all((progress.getState() == QUEST_PROGRESS_STATE.COMPLETED for progress in mainProgresses.itervalues()))


def _hasChangedMainProgresses(mainProgresses):
    return any((progress.isChanged() for progress in mainProgresses.itervalues()))


class DetailedProgressFormatter(ProgressesFormatter):

    def __init__(self, storage, personalMission):
        super(DetailedProgressFormatter, self).__init__(storage, personalMission.getDummyHeaderType())

    def hasProgressForReset(self):
        if self._storage:
            progresses = self._storage.getProgresses()
            if progresses:
                return any((progress.hasProgressForReset() for progress in progresses.itervalues()))
        return False


class PostBattleConditionsFormatter(object):
    __slots__ = ('__event', '__storage', '__wasMultiplied', '__wasFailed')

    def __init__(self, event, progressData):
        data = progressData or {}
        self.__event = event
        self.__storage = None
        self.__wasMultiplied = data.get('multiplied')
        self.__wasFailed = data.get('wasFailed')
        self.__storage = PostBattleProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), data.get('current'), event.isOneBattleQuest())
        return

    def getConditionsData(self, isMain):
        return {'statusText': self.__getStatusText(isMain),
         'text': self.__getQuestDescrText(isMain)}

    def getMultiplierDescription(self):
        if self.__wasMultiplied:
            for progress in self.__storage.getBodyProgresses().itervalues():
                multiplier = progress.getMultiplier()
                if multiplier:
                    return progress.getFormattedMultiplierValue(MULTIPLIER_SCOPE.POST_BATTLE)

    def getFailedDescription(self):
        if self.__wasFailed:
            progresses = self.__storage.getBodyProgresses()
            progresses.update(self.__storage.getHeaderProgresses())
            for progress in progresses.itervalues():
                if progress.getProgressID() in self.__wasFailed:
                    return text_styles.concatStylesToSingleLine(text_styles.alert(i18n.makeString(BATTLE_RESULTS.PERSONALQUEST_FAILED_ATTENTION)), ' ', text_styles.main(i18n.makeString(BATTLE_RESULTS.PERSONALQUEST_FAILED_DESCR)))

    def __getQuestDescrText(self, isMain):
        if isMain:
            title = PERSONAL_MISSIONS.TASKDETAILSVIEW_MAINCONDITIONS
        else:
            title = PERSONAL_MISSIONS.TASKDETAILSVIEW_ADDITIONALCONDITIONS
        return _packCondition(title, self.__getStrConditions(isMain))

    def __getStrConditions(self, isMain):
        return '\n'.join([ progress.getDescription() for progress in self.__storage.getBodyProgresses(isMain).itervalues() ])

    def __getStatusText(self, isMain):
        statusConditionValues = self.__getStatusConditionValues(isMain)
        if statusConditionValues:
            current, goal, state = statusConditionValues
            currentStr = backport.getNiceNumberFormat(current)
            goalStr = backport.getIntegralFormat(goal)
            if state == QUEST_PROGRESS_STATE.COMPLETED:
                return ''.join([text_styles.bonusAppliedText(currentStr), text_styles.success(' / %s' % goalStr)])
            if state == QUEST_PROGRESS_STATE.FAILED:
                return ''.join([text_styles.error(currentStr), text_styles.failedStatusText(' / %s' % goalStr)])
            return ''.join([text_styles.stats(currentStr), text_styles.main(' / %s' % goalStr)])

    def __getStatusConditionValues(self, isMain):
        for progress in self.__storage.getBodyProgresses(isMain).itervalues():
            if progress.isCumulative():
                return (progress.getCurrent(), progress.getGoal(), progress.getState())

        for progress in self.__storage.getHeaderProgresses(isMain).itervalues():
            return (progress.getCurrent(), progress.getGoal(), progress.getState())

        return None


class PMTooltipConditionsFormatters(object):
    _CONDITION = namedtuple('_CONDITION', ['icon', 'title', 'isInOrGroup'])

    def format(self, event, isMain=None):
        storage = LobbyProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), event.getConditionsProgress(), event.isOneBattleQuest())
        sortedProgresses = sorted(storage.getBodyProgresses(isMain).itervalues(), key=lambda p: (not p.isMain(), p.getPriority()))
        return [ self._CONDITION(RES_ICONS.get90ConditionIcon(c.getIconID()), text_styles.main(c.getDescription()), c.isInOrGroup()) for c in sortedProgresses ]


class PMAwardScreenConditionsFormatter(ProgressesFormatter):
    MAIN_PROGRESS_DATA = 'mainHeaderProgressData'
    ADD_PROGRESS_DATA = 'addHeaderProgressData'
    MAIN_VALUE_DATA = 'mainConditions'
    ADD_VALUE_DATA = 'addConditions'

    def __init__(self, event):
        storage = LobbyProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), event.getConditionsProgress(), event.isOneBattleQuest())
        storage.markAsCompleted(event.isCompleted(), event.isFullCompleted())
        super(PMAwardScreenConditionsFormatter, self).__init__(storage, dummyHeaderType=event.getDummyHeaderType())

    def getConditionsData(self, main, add):
        result = {}
        if self._storage:
            headerProgresses = self._storage.getHeaderProgresses()
            bodyProgresses = self._storage.getBodyProgresses()
            mainBodyProgresses, addBodyProgresses = [], []
            if bodyProgresses:
                sortedProgresses = self._sortedBodyProgresses(bodyProgresses)
                for progress in sortedProgresses:
                    if progress.isMain():
                        mainBodyProgresses.append(progress)
                    addBodyProgresses.append(progress)

            if headerProgresses:
                mainIterateProgressData, addIterateProgressData = {}, {}
                mainHeaderProgress = findFirst(lambda p: p.isMain(), headerProgresses.itervalues())
                addHeaderProgress = findFirst(lambda p: not p.isMain(), headerProgresses.itervalues())
                if mainHeaderProgress:
                    mainIterateProgressData = self._getIterateData(mainHeaderProgress, first(mainBodyProgresses))
                if addHeaderProgress:
                    addIterateProgressData = self._getIterateData(addHeaderProgress, first(addBodyProgresses))
                if main and mainIterateProgressData:
                    result[self.MAIN_PROGRESS_DATA] = mainIterateProgressData
                if add and addIterateProgressData:
                    result[self.ADD_PROGRESS_DATA] = addIterateProgressData
            if main and self.MAIN_PROGRESS_DATA not in result:
                result[self.MAIN_VALUE_DATA] = self._getValueData(mainBodyProgresses)
            if add and self.ADD_PROGRESS_DATA not in result:
                result[self.ADD_VALUE_DATA] = self._getValueData(addBodyProgresses)
        return result

    def _getIterateData(self, headerProgress, bodyProgress):
        if headerProgress.getDisplayType() in (DISPLAY_TYPE.BIATHLON, DISPLAY_TYPE.SERIES, DISPLAY_TYPE.COUNTER):
            headerData = headerProgress.getHeaderData()
            headerData['valueTitle'] = bodyProgress.getTitle()
            headerData['conditionIcon'] = self._getIcon(bodyProgress.getIconID())
            return headerData
        return {}

    def _getValueData(self, progresses):
        result = []
        for progress in progresses:
            result.append(self._makeBodyProgressData(progress))

        return result

    @classmethod
    def _getIcon(cls, key):
        return RES_ICONS.get90ConditionIcon(key)

    @classmethod
    def _makeBodyProgressData(cls, progress):
        state = progress.getState()
        if not progress.isCumulative() and state != QUEST_PROGRESS_STATE.COMPLETED:
            state = QUEST_PROGRESS_STATE.FAILED
        title = progress.getTitle()
        tooltip = makeTooltip(title, progress.getDescription())
        return {'initData': {'title': text_styles.middleTitle(title),
                      'iconID': progress.getIconID(),
                      'progressType': progress.getProgressType(),
                      'tooltip': tooltip,
                      'isInOrGroup': progress.isInOrGroup()},
         'progressData': {'current': progress.getCurrent(),
                          'state': state,
                          'goal': progress.getGoal()}}


class PMCardConditionsFormatter(DetailedProgressFormatter):

    def __init__(self, event):
        storage = LobbyProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), event.getConditionsProgress(), event.isOneBattleQuest())
        if event.getDummyHeaderType() == DISPLAY_TYPE.NONE:
            if not event.isInProgress():
                storage.markAsCompleted(event.isCompleted(), event.isFullCompleted())
        elif not event.isInProgress() or not event.areTokensPawned():
            storage.markAsCompleted(event.isCompleted(), event.isFullCompleted())
        super(PMCardConditionsFormatter, self).__init__(storage, event)
