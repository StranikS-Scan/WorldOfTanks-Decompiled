# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/offbattle/context.py
from constants import FINISH_REASON
from gui.shared.utils import isPopupsWindowsOpenDisabled
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
    return doc_loader.loadDescriptorData(TUTORIAL_SETTINGS.BATTLE_V2)


class OffbattleStartReqs(context.StartReqs):

    def prepare(self, ctx):
        ctx.bonusCompleted = game_vars.getTutorialsCompleted()
        ctx.battlesCount = game_vars.getRandomBattlesCount()
        ctx.newbieBattlesCount = getServerSettings().get('newbieBattlesCount', 0)

    def process(self, descriptor, ctx):
        if ctx.cache.isFinished() and not ctx.restart:
            return False
        popupsWindowsDisabled = isPopupsWindowsOpenDisabled()
        if not ctx.byRequest and popupsWindowsDisabled:
            ctx.cache.setStartOnNextLogin(False)
            ctx.cache.setRefused(True).write()
            return False
        self.__validateFinishReason(ctx)
        return self.__validateTutorialState(ctx) if self.__validateTutorialsCompleted(ctx, descriptor) else self.__validateBattleCount(descriptor, ctx)

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
                return cache.getPlayerXPLevel() != PLAYER_XP_LEVEL.NEWBIE
            cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
            if cache.wasReset():
                cache.setRefused(True)
            return True

    def __validateBattleCount(self, descriptor, ctx):
        if ctx.battlesCount < ctx.newbieBattlesCount:
            chapter = descriptor.getChapter(descriptor.getInitialChapterID())
            if chapter is None or not chapter.isBonusReceived(ctx.bonusCompleted):
                return True
            return self.__validateTutorialState(ctx)
        else:
            ctx.cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
            return self.__validateTutorialState(ctx)

    def __validateTutorialState(self, ctx):
        cache = ctx.cache
        if ctx.restart:
            return True
        if not ctx.isFirstStart and not cache.isAfterBattle() and not ctx.restart:
            cache.setRefused(True).write()
            return False
        if cache.isRefused():
            received = ctx.globalFlags[GLOBAL_FLAG.ALL_BONUSES_RECEIVED]
            if not received and not ctx.isAfterBattle and cache.doStartOnNextLogin():
                cache.setRefused(False).write()
                return True
            return False
        if cache.isAfterBattle():
            return True
        result = not ctx.isAfterBattle and cache.doStartOnNextLogin()
        cache.setRefused(not result).write()
        return result


class OffbattleBonusesRequester(LobbyBonusesRequester):

    def __init__(self, completed, chapter=None):
        super(OffbattleBonusesRequester, self).__init__(completed)
        self.__chapter = chapter

    def getChapter(self, chapterID=None):
        return self.__chapter if self.__chapter is not None else self._data
