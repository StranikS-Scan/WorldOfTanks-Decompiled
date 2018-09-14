# Embedded file name: scripts/client/tutorial/control/offbattle/queries.py
from constants import FINISH_REASON
from tutorial.control import ContentQuery
from tutorial.control.battle.context import TRAINING_RESULT_KEY
from tutorial.control.battle.context import TRAINING_FINISH_REASON_KEY
from tutorial.control.context import GLOBAL_VAR, GLOBAL_FLAG, GlobalStorage
from tutorial.control.offbattle.context import OffBattleClientCtx
from tutorial.control.offbattle.context import getBattleDescriptor
from tutorial.settings import PLAYER_XP_LEVEL, TUTORIAL_AVG_SESSION_TIME
from helpers import i18n

class GreetingContent(ContentQuery):

    def invoke(self, content, _):
        result = []
        descriptor = getBattleDescriptor()
        if descriptor is None:
            return
        else:
            completed = self._bonuses.getCompleted()
            for chapter in descriptor:
                if chapter.hasBonus():
                    result.append({'values': chapter.getBonus().getValues(),
                     'received': chapter.isBonusReceived(completed)})

            content['bonuses'] = result
            content['timeNoteValue'] = content['timeNoteValue'].format(i18n.makeString('#battle_tutorial:labels/minutes', units=str(TUTORIAL_AVG_SESSION_TIME)))
            return


class TutorialQueueText(ContentQuery):

    def invoke(self, content, varID):
        avgTime = self.getVar(varID, default=0)
        inMin = round(avgTime / 60000)
        pointcuts = content['timePointcuts']
        if inMin < pointcuts[0]:
            minString = i18n.makeString('#battle_tutorial:labels/less_n_minutes', minutes=str(pointcuts[0]))
        else:
            filtered = filter(lambda pointcut: pointcut >= inMin, pointcuts)
            if len(filtered):
                minString = i18n.makeString('#battle_tutorial:labels/minutes', units=str(filtered[0]))
            else:
                minString = i18n.makeString('#battle_tutorial:labels/more_n_minutes', minutes=str(pointcuts[-1]))
        content['avgTimeText'] = content['avgTimeTextFormat'].format(minString)


def _getChaptersResults(descriptor, localCtx, received):
    result = []
    inBattle = localCtx.completed
    for chapter in descriptor:
        if chapter.hasBonus():
            result.append({'label': chapter.getTitle() + chapter.getDescription(),
             'done': chapter.isBonusReceived(inBattle),
             'bonus': chapter.getBonus().getValues(),
             'received': chapter.isBonusReceived(received)})

    return result


def getTrainingResultKeys(finished, ctx):
    resultKey = TRAINING_RESULT_KEY.FAILED
    finishKey = TRAINING_FINISH_REASON_KEY.FAILED
    if finished:
        resultKey = TRAINING_RESULT_KEY.FINISHED
        finishKey = TRAINING_FINISH_REASON_KEY.FINISHED
    elif ctx.finishReason > -1:
        if ctx.finishReason is FINISH_REASON.TIMEOUT:
            finishKey = TRAINING_FINISH_REASON_KEY.TIMEOUT
        elif ctx.finishReason is FINISH_REASON.EXTERMINATION and ctx.winnerTeam is not ctx.playerTeam:
            finishKey = TRAINING_FINISH_REASON_KEY.EXTERMINATION
    return (resultKey, finishKey)


class BattleFinalStatistic(ContentQuery):
    _isHistory = GlobalStorage(GLOBAL_FLAG.SHOW_HISTORY, False)

    def invoke(self, content, varID):
        localCtx = OffBattleClientCtx.fetch(self._cache)
        descriptor = getBattleDescriptor()
        if descriptor is None:
            return
        else:
            if self._isHistory:
                received = self.__getReceivedBonusesInHistory(descriptor, localCtx)
            else:
                received = self.getVar(varID, default=0)
            content['finished'] = descriptor.areAllBonusesReceived(localCtx.completed)
            content['areAllBonusesReceived'] = descriptor.areAllBonusesReceived(self._bonuses.getCompleted())
            content['arenaUniqueID'] = localCtx.arenaUniqueID
            content['isHistory'] = self._isHistory
            self.__addTotalResult(localCtx, content)
            self.__addChaptersProcess(descriptor, localCtx, received, content)
            if content['areAllBonusesReceived']:
                self._cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
            self._cache.setAfterBattle(False).write()
            return

    def __addTotalResult(self, ctx, content):
        totalKey, finishKey = getTrainingResultKeys(content['finished'], ctx)
        content['totalResult'] = i18n.makeString('#battle_tutorial:labels/training-result/{0:>s}'.format(totalKey))
        content['finishReason'] = i18n.makeString('#battle_tutorial:labels/finish-reason/{0:>s}'.format(finishKey))

    def __addChaptersProcess(self, descriptor, ctx, received, content):
        content['chapters'] = _getChaptersResults(descriptor, ctx, received)
        content['progressMask'] = descriptor.getProgress(ctx.completed)
        content['lastChapter'] = ctx.chapterIdx
        content['totalChapters'] = descriptor.getNumberOfChapters()
        return content

    def __getReceivedBonusesInHistory(self, descriptor, ctx):
        accCompleted = 0
        inBattle = 0
        received = 0
        if ctx.accCompleted > 0:
            accCompleted = ctx.accCompleted
        if ctx.completed > 0:
            inBattle = ctx.completed
        for chapter in descriptor:
            if chapter.hasBonus() and chapter.isBonusReceived(inBattle):
                bit = 1 << chapter.getBonusID()
                if accCompleted & bit == 0:
                    received |= bit

        return received


class BattleResultMessage(ContentQuery):
    _lastHistoryID = GlobalStorage(GLOBAL_VAR.LAST_HISTORY_ID, 0)

    def invoke(self, content, varID):
        received = self.getVar(varID, default=0)
        localCtx = OffBattleClientCtx.fetch(self._cache)
        self._lastHistoryID = localCtx.arenaUniqueID
        descriptor = getBattleDescriptor()
        if descriptor is None:
            return
        else:
            content.update(localCtx._asdict())
            resultKey, finishKey = getTrainingResultKeys(descriptor.areAllBonusesReceived(localCtx.completed), localCtx)
            content['resultKey'] = resultKey
            content['finishKey'] = finishKey
            content['chapters'] = _getChaptersResults(descriptor, localCtx, received)
            content['areAllBonusesReceived'] = descriptor.areAllBonusesReceived(self._bonuses.getCompleted())
            return
