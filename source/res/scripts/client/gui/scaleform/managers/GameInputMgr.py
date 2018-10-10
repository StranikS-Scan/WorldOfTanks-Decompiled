# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/GameInputMgr.py
import CommandMapping
from messenger.proto import proto_getter
from messenger.m_constants import PROTO_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.abstract.GameInputManagerMeta import GameInputManagerMeta
from gui.shared.utils.key_mapping import getScaleformKey
__author__ = 'd_dichkovsky'

class GameInputMgr(GameInputManagerMeta):

    def __init__(self):
        super(GameInputMgr, self).__init__()
        self.__voiceChatKey = self._getCurrentChatKey()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def handleGlobalKeyEvent(self, keyCode, eventType):
        LOG_DEBUG('GameInputMgr.handleGlobalKeyEvent', keyCode, eventType)
        if keyCode == self.__voiceChatKey:
            self.bwProto.voipController.setMicrophoneMute(True if eventType == 'keyUp' else False)

    def updateChatKeyHandlers(self, value=None):
        if value and self.__voiceChatKey != value:
            self._clearChatKeyHandlers()
            if value is None:
                self.__voiceChatKey = self._getCurrentChatKey()
            else:
                self.__voiceChatKey = value
            self._setupChatKeyHandlers()
        return

    def _populate(self):
        super(GameInputMgr, self)._populate()
        self._setupChatKeyHandlers()

    def _dispose(self):
        self._clearChatKeyHandlers()
        super(GameInputMgr, self)._dispose()

    def _getCurrentChatKey(self):
        return getScaleformKey(CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE'))

    def _setupChatKeyHandlers(self):
        self.as_addKeyHandlerS(self.__voiceChatKey, 'keyDown', True, 'keyUp')
        self.as_addKeyHandlerS(self.__voiceChatKey, 'keyUp', False, None)
        return

    def _clearChatKeyHandlers(self):
        self.as_clearKeyHandlerS(self.__voiceChatKey, 'keyDown')
        self.as_clearKeyHandlerS(self.__voiceChatKey, 'keyUp')
