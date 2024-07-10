# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/formatters.py
import typing
from collections import namedtuple
from constants import QUEST_PROGRESS_STATE
from gui.Scaleform.genConsts.QUEST_PROGRESS_BASE import QUEST_PROGRESS_BASE
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
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
        return self._bodyFormat(True) + self._bodyFormat(False) if isMain is None else self._bodyFormat(isMain)

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
    def _makeBodyProgressData(cls, progress, isLastProgress=False):
        return progress.getFullData()

    def _bodyFormat(self, isMain):
        result = []
        if not self._storage:
            return result
        progresses = self._storage.getBodyProgresses(isMain)
        lastProgressIdx = len(progresses) - 1
        for index, progress in enumerate(self._storage.sortProgresses(progresses.itervalues())):
            result.append(self._makeBodyProgressData(progress, index == lastProgressIdx))

        return result

    def __addDummyHeaderProgress(self, isMain):
        orderType = QUEST_PROGRESS_BASE.ADD_ORDER_TYPE
        key = PERSONAL_MISSIONS.CONDITIONS_UNLIMITED_LABEL_ADD
        if isMain:
            orderType = QUEST_PROGRESS_BASE.MAIN_ORDER_TYPE
            key = PERSONAL_MISSIONS.CONDITIONS_UNLIMITED_LABEL_MAIN
        return {'progressType': self._dummyHeaderType,
         'orderType': orderType,
         'header': i18n.makeString(key)}


class DetailedProgressFormatter(ProgressesFormatter):

    def __init__(self, storage, personalMission):
        super(DetailedProgressFormatter, self).__init__(storage, personalMission.getDummyHeaderType())

    def hasProgressForReset(self):
        if self._storage:
            progresses = self._storage.getProgresses()
            if progresses:
                return any((progress.hasProgressForReset() for progress in progresses.itervalues()))
        return False

    @classmethod
    def _makeBodyProgressData(cls, progress, isLastProgress=False):
        bodyProgressData = super(DetailedProgressFormatter, cls)._makeBodyProgressData(progress, isLastProgress)
        if not isLastProgress:
            bodyProgressData['initData']['multiplier'] = ''
        return bodyProgressData


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
        conditions = self.__getPureConditionsData(isMain)
        resRoot = R.strings.personal_missions.taskDetailsView
        titleText = backport.text(resRoot.mainConditions() if isMain else resRoot.additionalConditions())
        titleStatusValues = None if any((c['statusText'] for c in conditions)) else self.__getTitleStatusValues(isMain)
        return [self.__packTitle(titleText, titleStatusValues)] + conditions

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

    def __getPureConditionsData(self, isMain):
        return [ self.__packCondition(progress.getDescription(), self.__getPureConditionStatusValues(progress)) for progress in self.__storage.sortProgresses(self.__storage.getBodyProgresses(isMain).itervalues()) ]

    def __getPureConditionStatusValues(self, progress):
        return (progress.getCurrent(), progress.getGoal(), progress.getState()) if progress.isCumulative() else None

    def __getTitleStatusValues(self, isMain):
        for progress in self.__storage.getHeaderProgresses(isMain).itervalues():
            return (progress.getCurrent(), progress.getGoal(), progress.getState())

        return None

    def __packBlock(self, text, statusValues=None):
        return {'text': text,
         'statusText': self.__packStatusText(statusValues) if statusValues else ''}

    def __packCondition(self, conditionText, statusValues=None):
        return self.__packBlock(text_styles.main(conditionText), statusValues)

    def __packTitle(self, titleText, titleStatusValues=None):
        return self.__packBlock(text_styles.leadingText(text_styles.middleTitle(titleText), 1), titleStatusValues)

    def __packStatusText(self, statusConditionValues):
        current, goal, state = statusConditionValues
        currentStr = backport.getNiceNumberFormat(current)
        goalStr = backport.getIntegralFormat(goal)
        if state == QUEST_PROGRESS_STATE.COMPLETED:
            return ''.join([text_styles.bonusAppliedText(currentStr), text_styles.success(' / %s' % goalStr)])
        return ''.join([text_styles.error(currentStr), text_styles.failedStatusText(' / %s' % goalStr)]) if state == QUEST_PROGRESS_STATE.FAILED else ''.join([text_styles.stats(currentStr), text_styles.main(' / %s' % goalStr)])


class PMTooltipConditionsFormatters(object):
    _CONDITION = namedtuple('_CONDITION', ['icon', 'title', 'isInOrGroup'])

    def format(self, event, isMain=None):
        storage = LobbyProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), event.getConditionsProgress(), event.isOneBattleQuest())
        return [ self._CONDITION(RES_ICONS.get90ConditionIcon(c.getIconID()), text_styles.main(c.getDescription()), c.isInOrGroup()) for c in storage.sortProgresses(storage.getBodyProgresses(isMain).itervalues()) ]


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
                for progress in self._storage.sortProgresses(bodyProgresses.itervalues()):
                    if progress.isMain():
                        mainBodyProgresses.append(progress)
                    addBodyProgresses.append(progress)

            if headerProgresses:
                mainIterateProgressData, addIterateProgressData = {}, {}
                mainHeaderProgress = findFirst(lambda p: p.isMain(), headerProgresses.itervalues())
                addHeaderProgress = findFirst(lambda p: not p.isMain(), headerProgresses.itervalues())
                if mainHeaderProgress:
                    mainIterateProgressData = self._getIterateData(mainHeaderProgress, mainBodyProgresses)
                if addHeaderProgress:
                    addIterateProgressData = self._getIterateData(addHeaderProgress, addBodyProgresses)
                if main and mainIterateProgressData:
                    result[self.MAIN_PROGRESS_DATA] = mainIterateProgressData
                if add and addIterateProgressData:
                    result[self.ADD_PROGRESS_DATA] = addIterateProgressData
            if main and self.MAIN_PROGRESS_DATA not in result:
                result[self.MAIN_VALUE_DATA] = self._getValueData(mainBodyProgresses)
            if add and self.ADD_PROGRESS_DATA not in result:
                result[self.ADD_VALUE_DATA] = self._getValueData(addBodyProgresses)
        return result

    def _getIterateData(self, headerProgress, bodyProgresses):
        if headerProgress.getDisplayType() in (DISPLAY_TYPE.BIATHLON, DISPLAY_TYPE.SERIES, DISPLAY_TYPE.COUNTER):
            headerData = headerProgress.getHeaderData()
            headerData['valueTitle'] = first(bodyProgresses).getTitle()
            headerData['conditions'] = [ {'icon': self._getIcon(progress.getIconID()),
             'tooltip': makeTooltip(progress.getTitle(), progress.getDescription())} for progress in bodyProgresses ]
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
    def _makeBodyProgressData(cls, progress, isLastProgress=False):
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
