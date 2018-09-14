# Embedded file name: scripts/client/tutorial/control/lobby/context.py
import BigWorld
from AccountCommands import RES_TUTORIAL_DISABLED
from tutorial.control import context
from tutorial.logger import LOG_ERROR, LOG_REQUEST
from tutorial.settings import TUTORIAL_STOP_REASON

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
            LOG_ERROR('Bonus already is received.')
            return
        else:
            bonusID = chapter.getBonusID()
            self._isReceived = False
            waitingID = chapter.getBonusMessage()
            if not waitingID:
                waitingID = 'request-bonus'
            self._gui.showWaiting(waitingID)
            LOG_REQUEST('Sends request on adding tutorial bonuses to the server', bonusID)
            BigWorld.player().completeTutorial(bonusID, lambda resultID: self.__cb_onCompleteTutorial(bonusID, waitingID, resultID))
            return

    def __cb_onCompleteTutorial(self, bonusID, waitingID, resultID):
        if self._tutorial is not None and not self._tutorial.isStopped():
            self._gui.hideWaiting(waitingID)
        self._isReceived = True
        if resultID < 0:
            LOG_ERROR('Server return error on request completeTutorial', resultID, bonusID)
            if resultID == RES_TUTORIAL_DISABLED:
                errorKey = '#tutorial:messages/tutorial-disabled'
            else:
                errorKey = '#tutorial:messages/request-bonus-failed'
            if self._tutorial is not None and not self._tutorial.isStopped():
                self._gui.showI18nMessage(errorKey, msgType='Error')
                self._gui.hideWaiting()
                self._tutorial.stop(reason=TUTORIAL_STOP_REASON.CRITICAL_ERROR)
            return
        else:
            LOG_REQUEST('Player has been received bonuses', bonusID)
            self._completed |= 1 << bonusID
            return
