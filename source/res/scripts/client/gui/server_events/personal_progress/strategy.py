# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_progress/strategy.py
import typing
from constants import QUEST_PROGRESS_STATE
from gui.Scaleform.genConsts.QUEST_PROGRESS_BASE import QUEST_PROGRESS_BASE
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.shared.formatters import text_styles
from helpers import i18n

class IProgressGetter(object):

    @classmethod
    def getGoal(cls, progress):
        raise NotImplementedError

    @classmethod
    def getCurrent(cls, progress):
        raise NotImplementedError


class BinaryProgressGetter(IProgressGetter):
    MAX_GOAL_VALUE = 1

    @classmethod
    def getGoal(cls, progress):
        return cls.MAX_GOAL_VALUE

    @classmethod
    def getCurrent(cls, progress):
        return int(progress.getState() == QUEST_PROGRESS_STATE.COMPLETED)


class ValueProgressGetter(IProgressGetter):

    @classmethod
    def getGoal(cls, progress):
        return progress.getGoal()

    @classmethod
    def getCurrent(cls, progress):
        return progress.getGoal() if progress.getState() == QUEST_PROGRESS_STATE.COMPLETED else int(min(progress.getValue(), progress.getGoal()))


class CounterProgressGetter(IProgressGetter):

    @classmethod
    def getGoal(cls, progress):
        return progress.getTotalGoal()

    @classmethod
    def getCurrent(cls, progress):
        totalGoal = progress.getTotalGoal()
        if progress.getState() == QUEST_PROGRESS_STATE.COMPLETED:
            return totalGoal
        totalCount = progress.getTotalCount()
        restUniqueElementsCount = progress.getUniqueGoal() - progress.getUniqueCount()
        return int(min(totalCount, totalGoal - restUniqueElementsCount))


class BiathlonProgressGetter(IProgressGetter):

    @classmethod
    def getGoal(cls, progress):
        return progress.getGoal()

    @classmethod
    def getCurrent(cls, progress):
        return progress.getGoal() if progress.getState() == QUEST_PROGRESS_STATE.COMPLETED else progress.getSuccessfullBattles()

    @classmethod
    def getBiathlonProgress(cls, progress):
        if progress.getState() == QUEST_PROGRESS_STATE.FAILED:
            return [QUEST_PROGRESS_BASE.HEADER_PROGRESS_BLOCK_FAILED] * progress.getBattlesLimit()
        if progress.getState() == QUEST_PROGRESS_STATE.COMPLETED:
            return tuple([QUEST_PROGRESS_BASE.HEADER_PROGRESS_BLOCK_COMPLETED] * progress.getBattlesLimit())
        result = []
        battles = progress.getBattles()
        battlesCount = len(battles)
        for i in range(progress.getBattlesLimit()):
            if i < battlesCount:
                if battles[i]:
                    result.append(QUEST_PROGRESS_BASE.HEADER_PROGRESS_BLOCK_COMPLETED)
                else:
                    result.append(QUEST_PROGRESS_BASE.HEADER_PROGRESS_BLOCK_FAILED)
            result.append(QUEST_PROGRESS_BASE.HEADER_PROGRESS_BLOCK_NOT_STARTED)

        return result


class ILabelGetter(object):

    @classmethod
    def getBottomLabel(cls, progress):
        if progress.getState() == QUEST_PROGRESS_STATE.FAILED:
            return text_styles.error(PERSONAL_MISSIONS.CONDITIONS_FAILED_BOTTOMLABEL)
        return cls._getCompleteLabel(progress) if progress.getState() == QUEST_PROGRESS_STATE.COMPLETED else i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_CURRENTPROGRESS_BOTTOMLABEL, currentProgress='%s / %s' % (text_styles.stats(progress.getCurrent()), progress.getGoal()))

    @classmethod
    def _getCompleteLabel(cls, progress):
        currentProgress = '%s / %s' % (text_styles.bonusAppliedText(progress.getCurrent()), text_styles.success(progress.getGoal()))
        label = i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_CURRENTPROGRESS_BOTTOMLABEL, currentProgress=currentProgress)
        status = text_styles.bonusAppliedText(PERSONAL_MISSIONS.CONDITIONS_COMPLETED_BOTTOMLABEL)
        return '%s      %s' % (label, status)

    @classmethod
    def getHeaderLabel(cls, progress):
        raise NotImplementedError


class BiathlonLabelGetter(ILabelGetter):

    @classmethod
    def getHeaderLabel(cls, progress):
        key = PERSONAL_MISSIONS.CONDITIONS_BIATHLON_LABEL_ADD
        if progress.isMain():
            key = PERSONAL_MISSIONS.CONDITIONS_BIATHLON_LABEL_MAIN
        return i18n.makeString(key, goal=progress.getGoal(), limit=progress.getBattlesLimit())

    @classmethod
    def _getCompleteLabel(cls, progress):
        return text_styles.bonusAppliedText(PERSONAL_MISSIONS.CONDITIONS_COMPLETED_BOTTOMLABEL)


class CounterLabelGetter(ILabelGetter):

    @classmethod
    def getHeaderLabel(cls, progress):
        key = PERSONAL_MISSIONS.CONDITIONS_COUNTER_LABEL_ADD
        if progress.isMain():
            key = PERSONAL_MISSIONS.CONDITIONS_COUNTER_LABEL_MAIN
        return i18n.makeString(key, count=progress.getGoal())


class SeriesLabelGetter(ILabelGetter):

    @classmethod
    def getHeaderLabel(cls, progress):
        key = PERSONAL_MISSIONS.CONDITIONS_SERIES_LABEL_ADD
        if progress.isMain():
            key = PERSONAL_MISSIONS.CONDITIONS_SERIES_LABEL_MAIN
        return i18n.makeString(key, count=progress.getGoal())


class LimitedTriesLabelGetter(ILabelGetter):

    @classmethod
    def getHeaderLabel(cls, progress):
        key = PERSONAL_MISSIONS.CONDITIONS_LIMITED_LABEL_ADD
        if progress.isMain():
            key = PERSONAL_MISSIONS.CONDITIONS_LIMITED_LABEL_MAIN
        return i18n.makeString(key, count=progress.getGoal())

    @classmethod
    def getBottomLabel(cls, progress):
        return i18n.makeString(PERSONAL_MISSIONS.CONDITIONS_BATTLESLEFT_BOTTOMLABEL, count=progress.getRest())
