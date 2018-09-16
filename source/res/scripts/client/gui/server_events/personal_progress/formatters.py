# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/formatters.py
from collections import namedtuple
import BigWorld
from constants import QUEST_PROGRESS_STATE
from gui.Scaleform.genConsts.QUEST_PROGRESS_BASE import QUEST_PROGRESS_BASE
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.cond_formatters.mixed_formatters import StringPersonalMissionConditionsFormatter
from gui.server_events.personal_progress.storage import PostBattleProgressStorage, LobbyProgressStorage
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
from personal_missions_constants import DISPLAY_TYPE
from shared_utils import first

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
                for progress in sorted(progresses.itervalues(), key=lambda p: p.isMain(), reverse=True):
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

    def bodyFormat(self, isMain=None):
        result = []
        if self._storage:
            progresses = self._storage.getBodyProgresses(isMain)
            if progresses:
                for progress in sorted(progresses.itervalues(), key=lambda p: p.isMain(), reverse=True):
                    result.append(self._makeBodyProgressData(progress))

        return result


class PostBattleConditionsFormatter(object):
    __slots__ = ('__event', '__storage', '__strConditionsFormatter', '__wasMultiplied', '__hasBattleProgress')

    def __init__(self, event, progressData):
        data = progressData or {}
        self.__event = event
        self.__storage = None
        self.__strConditionsFormatter = StringPersonalMissionConditionsFormatter()
        self.__wasMultiplied = data.get('multiplied')
        self.__hasBattleProgress = event.hasBattleProgress()
        if self.__hasBattleProgress:
            self.__storage = PostBattleProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), data.get('current'))
        return

    def getConditionsData(self, isMain):
        return {'statusText': self.__getStatusText(isMain),
         'text': self.__getQuestDescrText(isMain)}

    def getMultiplierDescription(self):
        if self.__wasMultiplied and self.__hasBattleProgress:
            for progress in self.__storage.getBodyProgresses().itervalues():
                multiplier = progress.getMultiplier()
                if multiplier:
                    return progress.getFormattedMultiplierValue('postBattle')

    def __getQuestDescrText(self, isMain):
        if isMain:
            title = PERSONAL_MISSIONS.TASKDETAILSVIEW_MAINCONDITIONS
        else:
            title = PERSONAL_MISSIONS.TASKDETAILSVIEW_ADDITIONALCONDITIONS
        return _packCondition(title, self.__getStrConditions(isMain))

    def __getStrConditions(self, isMain):
        if self.__hasBattleProgress:
            return '\n'.join([ progress.getDescription() for progress in self.__storage.getBodyProgresses(isMain).itervalues() ])
        return self.__strConditionsFormatter.format(self.__event, isMain)

    def __getStatusText(self, isMain):
        if not self.__hasBattleProgress:
            return ''
        statusConditionValues = self.__getStatusConditionValues(isMain)
        if statusConditionValues:
            current, goal, isCompleted = statusConditionValues
            currentStr = BigWorld.wg_getIntegralFormat(current)
            goalStr = BigWorld.wg_getIntegralFormat(goal)
            if isCompleted:
                return ''.join([text_styles.bonusAppliedText(currentStr), text_styles.success(' / %s' % goalStr)])
            return ''.join([text_styles.stats(currentStr), text_styles.main(' / %s' % goalStr)])

    def __getStatusConditionValues(self, isMain):
        for progress in self.__storage.getBodyProgresses(isMain).itervalues():
            if progress.isCumulative():
                return (progress.getCurrent(), progress.getGoal(), progress.getState() == QUEST_PROGRESS_STATE.COMPLETED)

        for progress in self.__storage.getHeaderProgresses(isMain).itervalues():
            return (progress.getCurrent(), progress.getGoal(), progress.getState() == QUEST_PROGRESS_STATE.COMPLETED)

        return None


class PM2TooltipConditionsFormatters(object):
    _CONDITION = namedtuple('_CONDITION', ['icon', 'title', 'isInOrGroup'])

    def format(self, event, isMain=None):
        storage = LobbyProgressStorage(event.getGeneralQuestID(), event.getConditionsConfig(), event.getConditionsProgress())
        return [ self._CONDITION(RES_ICONS.get90ConditionIcon(c.getIconID()), text_styles.main(c.getDescription()), False) for c in storage.getBodyProgresses(isMain).itervalues() ]


def _getSorage(event, checkInProgress):
    questCfg = event.getConditionsConfig()
    storage = None
    if questCfg:
        storage = LobbyProgressStorage(event.getGeneralQuestID(), questCfg, event.getConditionsProgress())
        if not event.isInProgress() or not checkInProgress:
            storage.markAsCompleted(event.isCompleted(), event.isFullCompleted())
    return storage


class PM2AwardScreenConditionsFormatter(ProgressesFormatter):

    def __init__(self, event):
        super(PM2AwardScreenConditionsFormatter, self).__init__(_getSorage(event, False), dummyHeaderType=event.getDummyHeaderType())

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
                      'tooltip': tooltip},
         'progressData': {'current': progress.getCurrent(),
                          'state': state,
                          'goal': progress.getGoal()}}


class PM2CardConditionsFormatter(DetailedProgressFormatter):

    def __init__(self, event):
        super(PM2CardConditionsFormatter, self).__init__(_getSorage(event, True), event)
