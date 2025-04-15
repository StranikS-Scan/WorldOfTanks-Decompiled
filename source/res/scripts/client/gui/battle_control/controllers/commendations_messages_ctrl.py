# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commendations_messages_ctrl.py
import logging
import typing
import BigWorld
import BattleReplay
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from commendations_common import CommendationHelpers
from constants import CommendationsState
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionMessage, ACTION_MESSAGE_TYPE
from skeletons.account_helpers.settings_core import IBattleCommunicationsSettings
from skeletons.gui.battle_session import IBattleSessionProvider
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.gui.game_control import ICommendationsController
if typing.TYPE_CHECKING:
    from commendations_common.CommendationHelpers import CommendationsSource
    from messenger.proto.bw_chat2.battle_chat_cmd import _ReceivedCmdDecorator
    from gui.battle_control.controllers.repositories import BattleSessionSetup
_logger = logging.getLogger(__name__)
_RECIPIENT_DURATION_MS = 5000
_SENDER_DURATION_MS = 2000
MESSAGE_STATE_RESOURCE_MAP = {CommendationsState.UNSENT: '',
 CommendationsState.SENT: 'comms_sent',
 CommendationsState.RECEIVED: 'comms_received',
 CommendationsState.MUTUAL: 'comms_mutual'}
MESSAGE_STATE_MARKER_MAP = {CommendationsState.UNSENT: '',
 CommendationsState.SENT: 'sendCommendation',
 CommendationsState.RECEIVED: 'gotCommendation',
 CommendationsState.MUTUAL: 'mutualCommendation'}

class _CommendationsActionMessage(ClientActionMessage):

    def __init__(self, message, iconName):
        ClientActionMessage.__init__(self, msg=message, type_=ACTION_MESSAGE_TYPE.COMMENDATIONS)
        self._iconName = iconName

    def getIconName(self):
        return self._iconName


class CommendationsMessagesController(IBattleController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __battleComSettings = dependency.descriptor(IBattleCommunicationsSettings)
    __commendationsCtrl = dependency.descriptor(ICommendationsController)

    def __init__(self, setup):
        super(CommendationsMessagesController, self).__init__()
        self._arena = setup.arenaEntity
        self.__isActive = False

    def startControl(self, *args):
        self.__battleComSettings.onChanged += self._onConfigChanged
        self.__commendationsCtrl.onSettingsChanged += self._onConfigChanged
        self.__isActive = self.__battleComSettings.isEnabled and self.__commendationsCtrl.isCommendationsEnabled
        if not self.__isActive:
            return
        self._activateListeners()

    def stopControl(self):
        self.__battleComSettings.onChanged -= self._onConfigChanged
        self.__commendationsCtrl.onSettingsChanged -= self._onConfigChanged
        self._deactivateListeners()

    def getControllerID(self):
        return BATTLE_CTRL_ID.COMMENDATIONS_MESSAGES_CTRL

    def sendCommendations(self, targetID, source):
        if not self.__commendationsCtrl.isCommendationsEnabled:
            return
        cmpt = CommendationHelpers.getAvatarComponent(BigWorld.player())
        cmpt.sendCommendation(targetID, source)

    def _activateListeners(self):
        g_messengerEvents.channels.onCommandReceived += self._onCommandReceived
        BattleReplay.g_replayCtrl.onCommandReceived += self._onCommandReceived

    def _deactivateListeners(self):
        g_messengerEvents.channels.onCommandReceived -= self._onCommandReceived
        BattleReplay.g_replayCtrl.onCommandReceived -= self._onCommandReceived

    def _canHandleCommand(self, cmd):
        if not cmd.getCommandType() == MESSENGER_COMMAND_TYPE.BATTLE:
            return False
        battleCommand = _ACTIONS.battleChatCommandFromActionID(cmd.getID())
        isCommendationCommand = battleCommand.name == BATTLE_CHAT_COMMAND_NAMES.COMMENDATION if battleCommand else False
        return isCommendationCommand

    def _canShowFeedback(self, cmd):
        return not cmd.isReceiver() or self.__battleComSettings.showCommendationsFeedbackOnReceive

    def _onCommandReceived(self, cmd):
        if not self.__commendationsCtrl.isCommendationsEnabled:
            return
        if not (self._canShowFeedback(cmd) and self._canHandleCommand(cmd) and self.__isActive):
            return
        vehicleID = 0
        durationMS = _SENDER_DURATION_MS
        messageState = cmd.getCommendationState()
        resourceName = MESSAGE_STATE_RESOURCE_MAP[messageState]
        actionMarker = MESSAGE_STATE_MARKER_MAP[messageState]
        if cmd.isReceiver():
            vehicleID = cmd.getSenderVehID()
            durationMS = _RECIPIENT_DURATION_MS
        elif cmd.isSender():
            vehicleID = cmd.getFirstTargetID()
        if not (resourceName and vehicleID):
            _logger.warning('Missing chat args for command: resourceName=%s, vehicleID=%s', resourceName, vehicleID)
            return
        self._addToChat(vehicleID, resourceName)
        self._arena.onUpdatePriorityChatCommand(vehicleID, actionMarker, durationMS)

    def _addToChat(self, targetID, resourceName):
        _logger.debug('[COMMS] messageReceived: targetID=%s, resourceName=%s', targetID, resourceName)
        playerName = self.__sessionProvider.getCtx().getPlayerFullName(vID=targetID)
        g_messengerEvents.onCustomMessage(_CommendationsActionMessage(backport.text(R.strings.messenger.client.commendations.dyn(resourceName)(), player=playerName), iconName=resourceName))

    def _onConfigChanged(self):
        self.__isActive = self.__battleComSettings.isEnabled and self.__commendationsCtrl.isCommendationsEnabled
        if self.__isActive:
            self._activateListeners()
        else:
            self._deactivateListeners()
