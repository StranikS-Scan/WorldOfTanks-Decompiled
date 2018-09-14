# Embedded file name: scripts/client/gui/Scaleform/managers/GameInputMgr.py
import Keys
import CommandMapping
import VOIP
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.abstract.GameInputManagerMeta import GameInputManagerMeta
from gui.shared.utils.key_mapping import getScaleformKey
__author__ = 'd_dichkovsky'

class GameInputMgr(GameInputManagerMeta):

    def __init__(self):
        super(GameInputMgr, self).__init__()
        self.__voiceChatKey = self._getCurrentChatKey()

    def handleGlobalKeyEvent(self, keyCode, eventType):
        LOG_DEBUG('GameInputMgr.handleGlobalKeyEvent', keyCode, eventType)
        if keyCode == self.__voiceChatKey and VOIP.getVOIPManager().getCurrentChannel():
            VOIP.getVOIPManager().setMicMute(True if eventType == 'keyUp' else False)

    def updateChatKeyHandlers(self, value = None):
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
