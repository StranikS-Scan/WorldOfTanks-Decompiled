# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_notifier_ctrl.py
import logging
from PlayerEvents import g_playerEvents
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class IBattleNotifierListener(object):

    def resultsNotificationReceived(self, message):
        pass


class BattleNotifierController(ViewComponentsController):
    __slots__ = ('__weakref__', '__enabled')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(BattleNotifierController, self).__init__()
        self.__enabled = False

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_NOTIFIER

    def startControl(self):
        _logger.debug('[BattleNotifierController PY] __startControl!')
        channel = g_messengerEvents.serviceChannel
        channel.onChatMessageReceived += self.__onChatMessage
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        self.__enabled = True

    def stopControl(self):
        channel = g_messengerEvents.serviceChannel
        channel.onChatMessageReceived -= self.__onChatMessage
        g_playerEvents.onRoundFinished -= self.__onRoundFinished

    def __onRoundFinished(self, winningTeam, reason, extraData):
        self.__enabled = False

    def __onChatMessage(self, clientID, message):
        if message.type == 2 and self.__enabled:
            for component in self._viewComponents:
                component.resultsNotificationReceived(message)


def createBattleNotifierController(setup):
    return BattleNotifierController(setup)
