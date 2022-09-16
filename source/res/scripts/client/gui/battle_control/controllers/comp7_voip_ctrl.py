# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/comp7_voip_ctrl.py
import logging
import typing
import BigWorld
import CommandMapping
import Keys
import VOIP
from constants import ARENA_PERIOD, IS_CHINA, REQUEST_COOLDOWN
from gui import g_keyEventHandlers
from gui.battle_control import event_dispatcher
from gui.battle_control.arena_info.interfaces import IComp7VOIPController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getKey, getReadableKey
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from VOIP.VOIPManager import VOIPManager
_logger = logging.getLogger(__name__)

class Comp7VOIPController(IComp7VOIPController):
    __slots__ = ('__messageShown', '__cooldownCallback')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self):
        self.__messageShown = False
        self.__cooldownCallback = None
        return

    @property
    def isVoipSupported(self):
        return not IS_CHINA and self.__VOIPManager.isVoiceSupported()

    @property
    def isVoipEnabled(self):
        return self.__VOIPManager.isEnabled()

    @property
    def isTeamChannelAvailable(self):
        return self.__comp7Controller.getModeSettings().createVivoxTeamChannels

    @property
    def isJoined(self):
        return self.__VOIPManager.isCurrentChannelEnabled()

    @property
    def isTeamVoipEnabled(self):
        return self.isVoipSupported and self.isVoipEnabled and self.isTeamChannelAvailable

    @property
    def __VOIPManager(self):
        return VOIP.getVOIPManager()

    def startControl(self, *_, **__):
        _logger.debug('[COMP7] Comp7VOIPController started.')
        self.__subscribe()

    def stopControl(self):
        _logger.debug('[COMP7] Comp7VOIPController stopped.')
        self.__unsubscribe()
        self.__messageShown = False
        self.__clearCooldown()

    def getControllerID(self):
        return BATTLE_CTRL_ID.COMP7_VOIP_CTRL

    def arenaLoadCompleted(self):
        self.__tryShowInfoMessage()

    def toggleChannelConnection(self):
        if self.__sessionProvider.isReplayPlaying:
            return
        elif self.__cooldownCallback is not None:
            _logger.info('Failed to toggle Comp7 team VOIP channel. Cooldown is in progress.')
            return
        elif not self.isTeamVoipEnabled:
            _logger.error('Failed to toggle Comp7 team VOIP channel. Joining is not allowed.')
            return
        else:
            event_dispatcher.toggleVoipChannelEnabled()
            self.__cooldownCallback = BigWorld.callback(REQUEST_COOLDOWN.POST_PROGRESSION_CELL + 1.0, self.__clearCooldown)
            return

    def __subscribe(self):
        g_keyEventHandlers.add(self.__handleKeyEvent)
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onChannelAvailable += self.__onChannelAvailable

    def __unsubscribe(self):
        g_keyEventHandlers.discard(self.__handleKeyEvent)
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onChannelAvailable -= self.__onChannelAvailable

    def __onChannelAvailable(self, *_, **__):
        self.__tryShowInfoMessage()

    def __tryShowInfoMessage(self):
        if self.__messageShown:
            return
        else:
            arenaPeriod = self.__sessionProvider.shared.arenaPeriod.getPeriod()
            if arenaPeriod <= ARENA_PERIOD.PREBATTLE:
                message = self.__getMessage()
                if message is not None:
                    g_messengerEvents.onWarningReceived(message)
                    self.__messageShown = True
            return

    def __getMessage(self):
        if not self.isVoipSupported or not self.isTeamChannelAvailable:
            return None
        else:
            command = CommandMapping.CMD_VOICECHAT_ENABLE
            resStr = R.strings.comp7.battleMessages
            if not self.isVoipEnabled:
                text = backport.text(resStr.withoutVOIP())
            elif getKey(command) == Keys.KEY_NONE:
                text = backport.text(resStr.specifyVOIP())
            else:
                text = backport.text(resStr.enableVOIP(), keyName=getReadableKey(command))
            return ClientActionMessage(text)

    def __handleKeyEvent(self, event):
        if not self.isTeamVoipEnabled:
            return
        if event.key == getKey(CommandMapping.CMD_VOICECHAT_ENABLE):
            if event.isKeyDown() and not event.isRepeatedEvent():
                self.toggleChannelConnection()

    def __clearCooldown(self):
        if self.__cooldownCallback is not None:
            BigWorld.cancelCallback(self.__cooldownCallback)
            self.__cooldownCallback = None
        return
