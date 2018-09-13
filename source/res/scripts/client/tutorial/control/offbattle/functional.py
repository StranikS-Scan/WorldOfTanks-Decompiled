# Embedded file name: scripts/client/tutorial/control/offbattle/functional.py
import BigWorld
import MusicController
from adisp import process
from gui import game_control
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.settings import FUNCTIONAL_EXIT
from tutorial.control import TutorialProxyHolder
from tutorial.control.functional import FunctionalEffect
from tutorial.control.offbattle.context import OffbattleBonusesRequester
from tutorial.control.offbattle.context import OffBattleClientCtx
from tutorial.control.offbattle.context import _getBattleDescriptor
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR, LOG_WARNING
from tutorial.settings import PLAYER_XP_LEVEL

class FunctionalEnterQueueEffect(FunctionalEffect):

    def triggerEffect(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doEffect(dispatcher)
        else:
            LOG_WARNING('Prebattle dispatcher is not defined')
        return

    @process
    def _doEffect(self, dispatcher):
        result = yield dispatcher.unlock(FUNCTIONAL_EXIT.BATTLE_TUTORIAL)
        if not result:
            self._tutorial.refuse()
            return
        else:
            enqueue = getattr(BigWorld.player(), 'enqueueTutorial', None)
            if enqueue is None:
                LOG_ERROR('BigWorld.player().enqueueTutorial not found')
                return
            activate = self._tutorial.getFlags().activateFlag
            flagID = self._effect.getTargetID()
            refuse = self._tutorial.refuse

            def enterToQueue(result):
                if result:
                    activate(flagID)
                    enqueue()
                else:
                    refuse()

            captcha = game_control.g_instance.captcha
            if captcha.isCaptchaRequired():
                captcha.showCaptcha(enterToQueue)
            else:
                enterToQueue(True)
            return


class FunctionalExitQueueEffect(FunctionalEffect):

    def triggerEffect(self):
        dequeue = getattr(BigWorld.player(), 'dequeueTutorial', None)
        if dequeue is not None and callable(dequeue):
            self._tutorial.getFlags().deactivateFlag(self._effect.getTargetID())
            dequeue()
        else:
            LOG_ERROR('BigWorld.player().dequeueTutorial not found')
        return


class ContentChangedEvent(TutorialProxyHolder):

    def __init__(self, popUpID):
        super(ContentChangedEvent, self).__init__()
        self._popUpID = popUpID

    def fire(self, value):
        popUp = self._tutorial._data.getHasIDEntity(self._popUpID)
        if popUp is not None:
            content = popUp.getContent()
            if not popUp.isContentFull():
                self._tutorial.getVars().set(popUp.getVarRef(), value)
                query = self._tutorial._ctrlFactory.createContentQuery(popUp.getType())
                query.invoke(content, popUp.getVarRef())
            if not self._gui.playEffect(GUI_EFFECT_NAME.UPDATE_CONTENT, [content]):
                LOG_ERROR('PopUp content is not updated', self._popUpID)
        else:
            LOG_ERROR('PopUp not found', self._popUpID)
        return


class FunctionalRequestAllBonusesEffect(FunctionalEffect):

    def __init__(self, effect):
        super(FunctionalRequestAllBonusesEffect, self).__init__(effect)
        self.__requesters = []

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        self.__requesters = filter(lambda requester: requester.isStillRunning(), self.__requesters)
        return len(self.__requesters)

    def triggerEffect(self):
        localCtx = OffBattleClientCtx.fetch(self._cache)
        inBattle = localCtx.completed
        inStats = self._bonuses.getCompleted()
        descriptor = _getBattleDescriptor()
        if descriptor is None:
            return
        else:
            for chapter in descriptor:
                if chapter.hasBonus() and chapter.isBonusReceived(inBattle) and not chapter.isBonusReceived(inStats):
                    self.__requesters.append(OffbattleBonusesRequester(self._bonuses.getCompleted(), chapter=chapter))

            for requester in self.__requesters:
                requester.request()

            return


class FunctionalPlayMusicEffect(FunctionalEffect):

    def triggerEffect(self):
        if MusicController.g_musicController is not None:
            soundID = getattr(MusicController, self._effect.getTargetID(), None)
            if soundID is not None:
                MusicController.g_musicController.play(soundID)
            else:
                LOG_ERROR('Sound not found', self._effect.getTargetID())
        return


class FunctionalShowMessage4QueryEffect(FunctionalEffect):

    def triggerEffect(self):
        target = self.getTarget()
        if target is not None:
            content = {}
            query = self._tutorial._ctrlFactory.createContentQuery(target.getType())
            query.invoke(content, target.getVarRef())
            self._gui.showServiceMessage(content, target.getExtra())
        else:
            LOG_ERROR('Target not found', self._effect.getTargetID())
        return


class FunctionalRefuseTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        descriptor = _getBattleDescriptor()
        if descriptor is not None and descriptor.areAllBonusesReceived(self._bonuses.getCompleted()):
            self._cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL).write()
        self._tutorial.refuse()
        return

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False
