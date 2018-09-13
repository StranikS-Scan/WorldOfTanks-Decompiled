# Embedded file name: scripts/client/tutorial/control/lobby/context.py
import BigWorld
from AccountCommands import RES_TUTORIAL_DISABLED, RES_SUCCESS
import dossiers2
from tutorial.control import context
from tutorial.logger import LOG_DEBUG, LOG_ERROR
from tutorial.settings import TUTORIAL_STOP_REASON

class LobbyStartReqs(context.StartReqs):

    def isEnabled(self):
        return not self._ctx.cache.isFinished() or self._ctx.restart

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
        ctx.bonusCompleted = completed
        cache = ctx.cache
        if loader.tutorial._descriptor.areAllBonusesReceived(completed):
            cache.setFinished(True).write()
            loader._clear()
            self._clear()
            return
        if cache.isRefused():
            self._clear()
            if ctx.restart and not ctx.isInPrebattle:
                loader.tutorial.restart(ctx)
            else:
                loader.tutorial.pause(ctx)
            return
        if cache.isEmpty() and not completed:
            BigWorld.player().stats.get('dossier', self.__cb_onGetDossier)
        else:
            self._clear()
            if not cache.isAfterBattle():
                cache.setAfterBattle(loader.isAfterBattle)
            loader._doRun(ctx)

    def __cb_onGetDossier(self, resultID, dossierCD):
        loader, ctx = self._flush()
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error on request dossier', resultID, dossierCD)
            loader._clear()
            return
        dossierDescr = dossiers2.getAccountDossierDescr(dossierCD)
        if not dossierDescr['a15x15']['battlesCount']:
            loader._doRun(ctx)
        else:
            ctx.cache.setFinished(True).write()
            loader._clear()


class LobbyBonusesRequester(context.BonusesRequester):

    def __init__(self, completed):
        super(LobbyBonusesRequester, self).__init__(completed)
        self._isReceived = True

    def isStillRunning(self):
        return not self._isReceived

    def request(self, chapterID = None):
        chapter = self.getChapter(chapterID=chapterID)
        if chapter is None:
            LOG_ERROR('Chapter not found', chapterID)
            return
        elif not chapter.hasBonus():
            LOG_ERROR('Chapter has not bonus.')
            return
        elif chapter.isBonusReceived(self._completed):
            LOG_ERROR('Bonus already received.')
            return
        else:
            bonusID = chapter.getBonusID()
            self._isReceived = False
            waitingID = chapter.getBonusMessage()
            if not len(waitingID):
                waitingID = 'request-bonus'
            self._gui.showWaiting(waitingID)
            LOG_DEBUG('completeTutorial', bonusID)
            BigWorld.player().completeTutorial(bonusID, lambda resultID: self.__cb_onCompleteTutorial(bonusID, waitingID, resultID))
            return

    def __cb_onCompleteTutorial(self, bonusID, waitingID, resultID):
        if self._tutorial is not None and not self._tutorial._tutorialStopped:
            self._gui.hideWaiting(waitingID)
        self._isReceived = True
        if resultID < 0:
            LOG_ERROR('Server return error on request completeTutorial', resultID, bonusID)
            if resultID == RES_TUTORIAL_DISABLED:
                errorKey = '#tutorial:messages/tutorial-disabled'
            else:
                errorKey = '#tutorial:messages/request-bonus-failed'
            if self._tutorial is not None and not self._tutorial._tutorialStopped:
                self._gui.showI18nMessage(errorKey, msgType='Error')
                self._gui.hideWaiting()
                self._tutorial.stop(reason=TUTORIAL_STOP_REASON.CRITICAL_ERROR)
            return
        else:
            LOG_DEBUG('Received bonus', bonusID)
            self._completed |= 1 << bonusID
            return
