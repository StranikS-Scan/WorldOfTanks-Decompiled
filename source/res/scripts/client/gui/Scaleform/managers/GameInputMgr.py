# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/GameInputMgr.py
import typing
import Keys
import CommandMapping
from Event import Event
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.abstract.GameInputManagerMeta import GameInputManagerMeta
from gui.shared.utils.key_mapping import getScaleformKey
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
if typing.TYPE_CHECKING:
    from typing import Callable
_KEY_ESCAPE = getScaleformKey(Keys.KEY_ESCAPE)
_KEY_DOWN = 'keyDown'
_KEY_UP = 'keyUp'

class GameInputMgr(GameInputManagerMeta):

    def __init__(self):
        super(GameInputMgr, self).__init__()
        self.__voiceChatKey = self._getCurrentChatKey()
        self.onEscape = Event()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def handleGlobalKeyEvent(self, keyCode, eventType):
        LOG_DEBUG('GameInputMgr.handleGlobalKeyEvent', keyCode, eventType)
        if keyCode == self.__voiceChatKey:
            self.bwProto.voipController.setMicrophoneMute(True if eventType == _KEY_UP else False)
        if keyCode == _KEY_ESCAPE:
            self.onEscape()

    def updateChatKeyHandlers(self, value=None):
        if value and self.__voiceChatKey != value:
            self._clearChatKeyHandlers()
            if value is None:
                self.__voiceChatKey = self._getCurrentChatKey()
            else:
                self.__voiceChatKey = value
            self._setupChatKeyHandlers()
        return

    def addEscapeListener(self, listener):
        self.onEscape += listener
        if len(self.onEscape) == 1:
            self.as_addKeyHandlerS(_KEY_ESCAPE, _KEY_DOWN, True)

    def removeEscapeListener(self, listener):
        self.onEscape -= listener
        if not self.onEscape:
            self.as_clearKeyHandlerS(_KEY_ESCAPE, _KEY_DOWN)

    def setIgnoredKeyCode(self, keyCode):
        self.as_setIgnoredKeyCodeS(keyCode)

    def _populate(self):
        super(GameInputMgr, self)._populate()
        self._setupChatKeyHandlers()

    def _dispose(self):
        self._clearChatKeyHandlers()
        super(GameInputMgr, self)._dispose()

    def _getCurrentChatKey(self):
        return getScaleformKey(CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE'))

    def _setupChatKeyHandlers(self):
        self.as_addKeyHandlerS(self.__voiceChatKey, _KEY_DOWN, True, _KEY_UP)
        self.as_addKeyHandlerS(self.__voiceChatKey, _KEY_UP, False, None)
        return

    def _clearChatKeyHandlers(self):
        self.as_clearKeyHandlerS(self.__voiceChatKey, _KEY_DOWN)
        self.as_clearKeyHandlerS(self.__voiceChatKey, _KEY_UP)
