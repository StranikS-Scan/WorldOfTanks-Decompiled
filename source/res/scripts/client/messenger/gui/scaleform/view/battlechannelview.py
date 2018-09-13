# Embedded file name: scripts/client/messenger/gui/Scaleform/view/BattleChannelView.py
import weakref
from gui import makeHtmlString
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface
from messenger import g_settings
from messenger.gui.Scaleform import BTMS_COMMANDS
from messenger.m_constants import BATTLE_CHANNEL

class BattleChannelView(UIInterface):
    _lastReceiver = BATTLE_CHANNEL.TEAM[1]

    def __init__(self, sharedHistory, receiver):
        super(BattleChannelView, self).__init__()
        self._receiver = receiver
        self._channelID = 0
        self._controller = lambda : None
        self._sharedHistory = weakref.ref(sharedHistory)

    def populateUI(self, proxy):
        super(BattleChannelView, self).populateUI(proxy)
        self.uiHolder.addExternalCallbacks({BTMS_COMMANDS.CheckCooldownPeriod(): self.__onCheckCooldownPeriod,
         BTMS_COMMANDS.SendMessage(): self.__onSendChannelMessage,
         BTMS_COMMANDS.ReceiverChanged(): self.__onReceiverChanged})
        controller = self._controller()
        if controller and controller.getChannel().isJoined():
            self.setJoined()

    def dispossessUI(self):
        if self.uiHolder:
            self.uiHolder.removeExternalCallback(BTMS_COMMANDS.CheckCooldownPeriod(), self.__onCheckCooldownPeriod)
            self.uiHolder.removeExternalCallback(BTMS_COMMANDS.SendMessage(), self.__onSendChannelMessage)
            self.uiHolder.removeExternalCallback(BTMS_COMMANDS.ReceiverChanged(), self.__onReceiverChanged)
        super(BattleChannelView, self).dispossessUI()
        self._sharedHistory = lambda : None

    @classmethod
    def resetReceiver(cls):
        if not g_settings.userPrefs.storeReceiverInBattle:
            cls._lastReceiver = BATTLE_CHANNEL.TEAM[1]

    def setController(self, controller):
        channel = controller.getChannel()
        self._controller = weakref.ref(controller)
        self._channelID = channel.getID()
        if channel.isJoined():
            self.setJoined()

    def removeController(self):
        self._controller = lambda : None
        self._channelID = 0

    def setJoined(self):
        args = self.getRecvConfig()[:]
        args.insert(0, self._channelID)
        self.__flashCall(BTMS_COMMANDS.JoinToChannel(), args)

    def updateView(self):
        self.setJoined()

    def addMessage(self, message, isCurrentPlayer = False):
        history = self._sharedHistory()
        if history:
            history.addMessage(message, isCurrentPlayer)
        self.__flashCall(BTMS_COMMANDS.ReceiveMessage(), [self._channelID, message, isCurrentPlayer])

    def getRecvConfig(self):
        config = ['', 0, False]
        receivers = g_settings.battle.receivers
        controller = self._controller()
        isChatEnabled = controller.isBattleChatEnabled()
        if self._receiver in receivers:
            color = g_settings.getColorScheme('battle/receiver').getHexStr(self._receiver)
            inputColor = g_settings.getColorScheme('battle/message').getHexStr(self._receiver)
            receiver = receivers[self._receiver]._asdict()
            byDefault = False
            if g_settings.userPrefs.storeReceiverInBattle:
                byDefault = self._receiver == BattleChannelView._lastReceiver
            if isChatEnabled:
                recLabel = receiver['label'] % color
            else:
                recLabel = makeHtmlString('html_templates:battle', 'battleChatIsLocked', {})
            config = [recLabel,
             receiver['order'],
             byDefault,
             inputColor,
             isChatEnabled]
            config.extend(receiver['modifiers'])
        return config

    def __flashCall(self, funcName, args = None):
        if self.uiHolder:
            self.uiHolder.call(funcName, args)

    def __flashRespond(self, args = None):
        self.uiHolder.respond(args)

    def __onReceiverChanged(self, *args):
        parser = CommandArgsParser(self.__onReceiverChanged.__name__, 1, [long])
        channelID, = parser.parse(*args)
        if self._channelID == channelID:
            BattleChannelView._lastReceiver = self._receiver

    def __onCheckCooldownPeriod(self, *args):
        controller = self._controller()
        if controller is None:
            return
        else:
            parser = CommandArgsParser(self.__onCheckCooldownPeriod.__name__, 1, [long])
            channelID, = parser.parse(*args)
            if channelID == self._channelID:
                result, errorMsg = controller.canSendMessage()
                parser.addArgs([channelID, result])
                self.__flashRespond(parser.args())
                if not result:
                    message = g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': errorMsg})
                    history = self._sharedHistory()
                    if history:
                        history.addMessage(message, False)
                    self.__flashCall(BTMS_COMMANDS.ReceiveMessage(), [channelID, message, False])
            return

    def __onSendChannelMessage(self, *args):
        controller = self._controller()
        if controller is None:
            return
        else:
            parser = CommandArgsParser(self.__onSendChannelMessage.__name__, 2, [long])
            channelID, rawMsgText = parser.parse(*args)
            if self._channelID == channelID:
                controller.sendMessage(rawMsgText)
            return
