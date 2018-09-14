# Embedded file name: scripts/client/tutorial/control/offbattle/context.py
from constants import FINISH_REASON, IS_TUTORIAL_ENABLED
from tutorial import doc_loader
from tutorial.control import context, getServerSettings, game_vars
from tutorial.control.battle.context import ExtendedBattleClientCtx
from tutorial.control.context import GLOBAL_FLAG
from tutorial.control.lobby.context import LobbyBonusesRequester
from tutorial.logger import LOG_ERROR
from tutorial.settings import TUTORIAL_SETTINGS, PLAYER_XP_LEVEL

class OffBattleClientCtx(ExtendedBattleClientCtx):

    @classmethod
    def fetch(cls, cache):
        return cls.makeCtx(cache.getLocalCtx())


def getBattleDescriptor():
    return doc_loader.loadDescriptorData(TUTORIAL_SETTINGS.BATTLE)


class OffbattleStartReqs(context.StartReqs):

    def isEnabled(self):
        isTutorialEnabled = IS_TUTORIAL_ENABLED
        serverSettings = getServerSettings()
        if 'isTutorialEnabled' in serverSettings:
            isTutorialEnabled = serverSettings['isTutorialEnabled']
        return isTutorialEnabled

    def prepare(self, ctx):
        ctx.bonusCompleted = game_vars.getTutorialsCompleted()
        ctx.battlesCount = game_vars.getRandomBattlesCount()
        ctx.newbieBattlesCount = getServerSettings().get('newbieBattlesCount', 0)

    def process(self, descriptor, ctx):
        if ctx.cache.isFinished() and not ctx.restart:
            return False
        else:
            self.__validateFinishReason(ctx)
            if self.__validateTutorialsCompleted(ctx, descriptor):
                return self.__validateTutorialState(ctx)
            return self.__validateBattleCount(descriptor, ctx)

    def __validateFinishReason(self, ctx):
        cache = ctx.cache
        finishReason = OffBattleClientCtx.fetch(cache).finishReason
        if GLOBAL_FLAG.SHOW_HISTORY in ctx.globalFlags:
            isHistory = ctx.globalFlags[GLOBAL_FLAG.SHOW_HISTORY]
        else:
            isHistory = False
        if isHistory or not cache.isRefused() and ctx.isAfterBattle and finishReason not in (-1, FINISH_REASON.FAILURE):
            cache.setAfterBattle(True)
        else:
            cache.setAfterBattle(False)

    def __validateTutorialsCompleted(self, ctx, descriptor):
        cache = ctx.cache
        battleDesc = getBattleDescriptor()
        if battleDesc is None:
            LOG_ERROR('Battle tutorial is not defined.')
            return False
        else:
            received = battleDesc.areAllBonusesReceived(ctx.bonusCompleted)
            ctx.globalFlags[GLOBAL_FLAG.ALL_BONUSES_RECEIVED] = received
            if not received:
                if cache.getPlayerXPLevel() == PLAYER_XP_LEVEL.NEWBIE:
                    return False
                else:
                    return True
            else:
                cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
                if cache.wasReset():
                    cache.setRefused(True)
                return True
            return

    def __validateBattleCount(self, descriptor, ctx):
        if ctx.battlesCount < ctx.newbieBattlesCount:
            chapter = descriptor.getChapter(descriptor.getInitialChapterID())
            if chapter is None or not chapter.isBonusReceived(ctx.bonusCompleted):
                return True
            else:
                return self.__validateTutorialState(ctx)
        else:
            ctx.cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
            return self.__validateTutorialState(ctx)
        return

    def __validateTutorialState(self, ctx):
        cache = ctx.cache
        if ctx.restart:
            return True
        elif not ctx.isFirstStart and not cache.isAfterBattle() and not ctx.restart:
            cache.setRefused(True).write()
            return False
        else:
            if cache.isRefused():
                received = ctx.globalFlags[GLOBAL_FLAG.ALL_BONUSES_RECEIVED]
                if not received and not ctx.isAfterBattle and cache.doStartOnNextLogin():
                    cache.setRefused(False).write()
                    return True
                else:
                    return False
            if cache.isAfterBattle():
                return True
            result = not ctx.isAfterBattle and cache.doStartOnNextLogin()
            cache.setRefused(not result).write()
            return result


class OffbattleBonusesRequester(LobbyBonusesRequester):

    def __init__(self, completed, chapter = None):
        super(OffbattleBonusesRequester, self).__init__(completed)
        self.__chapter = chapter

    def getChapter(self, chapterID = None):
        if self.__chapter is not None:
            return self.__chapter
        else:
            return self._data
