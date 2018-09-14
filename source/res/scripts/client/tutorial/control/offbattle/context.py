# Embedded file name: scripts/client/tutorial/control/offbattle/context.py
import BigWorld
from AccountCommands import RES_SUCCESS
from constants import FINISH_REASON, IS_TUTORIAL_ENABLED
import dossiers2
from tutorial import doc_loader
from tutorial.control import context
from tutorial.control.battle.context import ExtendedBattleClientCtx
from tutorial.control.context import GlobalStorage, GLOBAL_FLAG
from tutorial.control.lobby.context import LobbyBonusesRequester
from tutorial.logger import LOG_ERROR
from tutorial.settings import TUTORIAL_SETTINGS, PLAYER_XP_LEVEL

class OffBattleClientCtx(ExtendedBattleClientCtx):

    @classmethod
    def fetch(cls, cache):
        return cls.makeCtx(cache.getLocalCtx())


def _getBattleDescriptor():
    return doc_loader.loadDescriptorData(TUTORIAL_SETTINGS.BATTLE.descriptorPath)


class OffbattleStartReqs(context.StartReqs):
    _isHistory = GlobalStorage(GLOBAL_FLAG.SHOW_HISTORY, False)
    _areAllBonusesReceived = GlobalStorage(GLOBAL_FLAG.ALL_BONUSES_RECEIVED, False)

    def isEnabled(self):
        isTutorialEnabled = IS_TUTORIAL_ENABLED
        player = BigWorld.player()
        if player is not None:
            serverSettings = getattr(player, 'serverSettings', {})
            if 'isTutorialEnabled' in serverSettings:
                isTutorialEnabled = serverSettings['isTutorialEnabled']
        return (not self._ctx.cache.isFinished() or self._ctx.restart) and isTutorialEnabled

    def process(self):
        BigWorld.player().stats.get('tutorialsCompleted', self.__cb_onGetTutorialsCompleted)

    def __cb_onGetTutorialsCompleted(self, resultID, completed):
        ctx = self._ctx
        loader = self._loader
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error on request tutorialsCompleted', resultID, completed)
            loader._clear()
            self._clear()
            return
        else:
            ctx.bonusCompleted = completed
            cache = ctx.cache
            battleDesc = _getBattleDescriptor()
            if battleDesc is None:
                LOG_ERROR('Battle tutorial is not defined.')
                loader._clear()
                self._clear()
                return
            finishReason = OffBattleClientCtx.fetch(cache).finishReason
            if self._isHistory or not cache.isRefused() and loader.isAfterBattle and finishReason not in [-1, FINISH_REASON.FAILURE]:
                cache.setAfterBattle(True)
            else:
                cache.setAfterBattle(False)
            self._areAllBonusesReceived = battleDesc.areAllBonusesReceived(completed)
            if not self._areAllBonusesReceived:
                if cache.getPlayerXPLevel() == PLAYER_XP_LEVEL.NEWBIE:
                    BigWorld.player().stats.get('dossier', self.__cb_onGetDossier)
                else:
                    self._clear()
                    self._resolveTutorialState(loader, ctx)
            else:
                cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
                if cache.wasReset():
                    cache.setRefused(True)
                self._clear()
                self._resolveTutorialState(loader, ctx)
            return

    def __cb_onGetDossier(self, resultID, dossierCD):
        loader, ctx = self._flush()
        cache = ctx.cache
        tutorial = loader.tutorial
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error on request dossier', resultID, dossierCD)
            loader._clear()
            return
        else:
            dossierDescr = dossiers2.getAccountDossierDescr(dossierCD)
            battlesCount = dossierDescr['a15x15']['battlesCount']
            threshold = BigWorld.player().serverSettings.get('newbieBattlesCount', 0)
            if battlesCount < threshold:
                descriptor = tutorial._descriptor
                chapter = descriptor.getChapter(descriptor.getInitialChapterID())
                if chapter is None or not chapter.isBonusReceived(ctx.bonusCompleted):
                    loader._doRun(ctx)
                else:
                    self._resolveTutorialState(loader, ctx)
            else:
                cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
                self._resolveTutorialState(loader, ctx)
            return

    def _resolveTutorialState(self, loader, ctx):
        cache = ctx.cache
        tutorial = loader.tutorial
        if (ctx.isInPrebattle or not ctx.isFirstStart and not cache.isAfterBattle()) and not ctx.restart:
            tutorial.pause(ctx)
            cache.setRefused(True).write()
            return
        if cache.isRefused():
            if ctx.restart:
                tutorial.restart(ctx)
            elif not self._areAllBonusesReceived and not loader.isAfterBattle and cache.doStartOnNextLogin():
                loader._doRun(ctx)
            else:
                tutorial.pause(ctx)
            return
        if cache.isAfterBattle():
            loader._doRun(ctx)
        elif not loader.isAfterBattle and cache.doStartOnNextLogin():
            loader._doRun(ctx)
        else:
            tutorial.pause(ctx)
            cache.setRefused(True).write()


class OffbattleBonusesRequester(LobbyBonusesRequester):

    def __init__(self, completed, chapter = None):
        super(OffbattleBonusesRequester, self).__init__(completed)
        self.__chapter = chapter

    def getChapter(self, chapterID = None):
        if self.__chapter is not None:
            return self.__chapter
        else:
            return self._data
