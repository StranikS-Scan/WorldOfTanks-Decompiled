# Embedded file name: scripts/client/tutorial/control/offbattle/functional.py
import collections
import MusicController
import ResMgr
from adisp import process
from constants import QUEUE_TYPE
from gui.prb_control.context import pre_queue_ctx
from gui.prb_control.functional.battle_tutorial import TutorialPreQueueEntry
from helpers.i18n import makeString as _ms
from gui.game_control import getBrowserCtrl
from gui.prb_control.dispatcher import g_prbLoader
from tutorial.control import TutorialProxyHolder
from tutorial.control.context import GLOBAL_VAR, GlobalStorage
from tutorial.control.functional import FunctionalEffect
from tutorial.control.offbattle.context import OffbattleBonusesRequester
from tutorial.control.offbattle.context import OffBattleClientCtx
from tutorial.control.offbattle.context import getBattleDescriptor
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR, LOG_WARNING
from tutorial.settings import PLAYER_XP_LEVEL

class FunctionalEnterQueueEffect(FunctionalEffect):

    def triggerEffect(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            if state.isInPreQueue(QUEUE_TYPE.TUTORIAL):
                self._doEffect(dispatcher)
            else:
                self._doSelect(dispatcher)
        else:
            LOG_WARNING('Prebattle dispatcher is not defined')
            self._tutorial.refuse()
        return

    @process
    def _doSelect(self, dispatcher):
        result = yield dispatcher.select(TutorialPreQueueEntry())
        if result:
            self._doEffect(dispatcher)

    @process
    def _doEffect(self, dispatcher):
        result = yield dispatcher.sendPreQueueRequest(pre_queue_ctx.QueueCtx())
        if not result:
            self._tutorial.refuse()


class FunctionalExitQueueEffect(FunctionalEffect):

    def triggerEffect(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doEffect(dispatcher)
        else:
            LOG_WARNING('Prebattle dispatcher is not defined')
        self._tutorial.getFlags().deactivateFlag(self._effect.getTargetID())
        return

    @process
    def _doEffect(self, dispatcher):
        result = yield dispatcher.sendPreQueueRequest(pre_queue_ctx.DequeueCtx())
        if result:
            self._tutorial.getFlags().deactivateFlag(self._effect.getTargetID())


class ContentChangedEvent(TutorialProxyHolder):

    def __init__(self, popUpID):
        super(ContentChangedEvent, self).__init__()
        self._popUpID = popUpID

    def fire(self, value):
        popUp = self._data.getHasIDEntity(self._popUpID)
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
        descriptor = getBattleDescriptor()
        if descriptor is None:
            return
        else:
            for chapter in descriptor:
                if chapter.hasBonus() and chapter.isBonusReceived(inBattle) and not chapter.isBonusReceived(inStats):
                    self.__requesters.append(OffbattleBonusesRequester(self._bonuses.getCompleted(), chapter=chapter))

            for requester in self.__requesters:
                requester.request()

            return


class FunctionalOpenInternalBrowser(FunctionalEffect):

    def triggerEffect(self):
        browserID = self._effect.getTargetID()
        if getBrowserCtrl().getBrowser(browserID) is None:
            getBrowserCtrl().load(url='file:///{0}'.format(ResMgr.resolveToAbsolutePath('gui/html/video_tutorial/index_{0}.html'.format(_ms('#settings:LANGUAGE_CODE')))), title=_ms('#miniclient:tutorial/video/title'), showCloseBtn=True, showActionBtn=False, browserSize=(780, 470), browserID=browserID)(lambda success: True)
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
    _messagesIDs = GlobalStorage(GLOBAL_VAR.SERVICE_MESSAGES_IDS, [])

    def triggerEffect(self):
        target = self.getTarget()
        if target is not None:
            content = {}
            query = self._tutorial._ctrlFactory.createContentQuery(target.getType())
            query.invoke(content, target.getVarRef())
            messageID = self._gui.showServiceMessage(content, target.getExtra())
            if messageID:
                ids = self._messagesIDs
                if isinstance(ids, collections.Iterable):
                    ids.append(messageID)
        else:
            LOG_ERROR('Target not found', self._effect.getTargetID())
        return


class FunctionalRefuseTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        descriptor = getBattleDescriptor()
        if descriptor is not None and descriptor.areAllBonusesReceived(self._bonuses.getCompleted()):
            self._cache.setPlayerXPLevel(PLAYER_XP_LEVEL.NORMAL)
        self._cache.setAfterBattle(False).write()
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doLeaveAction(pre_queue_ctx.LeavePreQueueCtx())
        else:
            LOG_WARNING('Prebattle dispatcher is not defined')
        self._tutorial.refuse()
        return

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False
