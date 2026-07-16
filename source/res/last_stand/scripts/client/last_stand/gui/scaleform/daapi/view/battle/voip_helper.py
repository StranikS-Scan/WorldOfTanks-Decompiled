# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/voip_helper.py
from __future__ import absolute_import
import weakref
import typing
import CommandMapping
import Keys
import SoundGroups
import VOIP
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from gui import g_keyEventHandlers, InputHandler
from gui.shared.utils.key_mapping import getKey, getReadableKey
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from account_helpers.settings_core.settings_constants import SOUND
from gui.impl import backport
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from last_stand.gui.battle_control.interfaces import ILSVOIPController
_VOICE_CHAT_ENTER_SOUND_EVENT = 'ev_last_stand_voicechat_enter'
_VOICE_CHAT_EXIT_SOUND_EVENT = 'ev_last_stand_voicechat_exit'
_KEY_NONE_TEXT = backport.text(R.strings.ingame_gui.voice_chat.hotkeyUndefined())

class LSVoipHelper(object):
    __slots__ = ('__component', '__isAvailable')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, component):
        self.__component = weakref.ref(component)
        self.__isAvailable = False

    @property
    def isJoined(self):
        voipCtrl = self._voipController
        return voipCtrl is not None and voipCtrl.isJoined

    @property
    def isEnabled(self):
        voipCtrl = self._voipController
        return voipCtrl is not None and voipCtrl.isVoipEnabled

    @property
    def _voipController(self):
        return self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_VOIP_CTRL)

    def _playsound(self):
        if not self._voipController.isTeamVoipEnabled:
            return
        soundEvent = _VOICE_CHAT_ENTER_SOUND_EVENT if not self.isJoined else _VOICE_CHAT_EXIT_SOUND_EVENT
        SoundGroups.g_instance.playSound2D(soundEvent)

    def populate(self):
        self.__isAvailable = self._voipController.isTeamChannelAvailable if self._voipController else False
        component = self.__component()
        if component:
            component.as_setVoiceChatAvailableS(self.__isAvailable)
        g_keyEventHandlers.add(self.__handleVoipStatusKeyEvent)
        if not self.__isAvailable:
            return
        self._updateMapping()
        self.__update()
        self.__subscribe()

    def dispose(self):
        if self.__isAvailable:
            self.__unsubscribe()
        g_keyEventHandlers.discard(self.__handleVoipStatusKeyEvent)
        self.__component = lambda : None

    def __handleVoipStatusKeyEvent(self, event):
        if event.key == getKey(CommandMapping.CMD_VOICECHAT_ENABLE):
            if event.isKeyDown() and not event.isRepeatedEvent():
                self.toggleChannelConnection()

    def __handleKeyDown(self, event):
        component = self.__component()
        if event.key == getKey(CommandMapping.CMD_VOICECHAT_MUTE) and component:
            component.as_setIsTalkS(True)

    def __handleKeyUp(self, event):
        component = self.__component()
        if event.key == getKey(CommandMapping.CMD_VOICECHAT_MUTE) and component:
            component.as_setIsTalkS(False)

    def _updateMapping(self, *args):
        component = self.__component()
        if not component:
            return
        chatBind = self.__getKeyBind(CommandMapping.CMD_VOICECHAT_ENABLE)
        talkBind = self.__getKeyBind(CommandMapping.CMD_VOICECHAT_MUTE)
        component.as_setVoiceChatBindingsS(chatBind, talkBind)

    def _onSettingsChanged(self, diff):
        if SOUND.VOIP_ENABLE in diff:
            self.__update()

    def toggleMute(self, isMuted):
        voipCtrl = self._voipController
        if not voipCtrl:
            return
        voipCtrl.toggleMute(isMuted)

    def toggleChannelConnection(self):
        voipCtrl = self._voipController
        if not voipCtrl:
            return
        self._playsound()
        voipCtrl.toggleChannelConnection()

    def __subscribe(self):
        CommandMapping.g_instance.onMappingChanged += self._updateMapping
        InputHandler.g_instance.onKeyDown += self.__handleKeyDown
        InputHandler.g_instance.onKeyUp += self.__handleKeyUp
        self.__settingsCore.onSettingsChanged += self._onSettingsChanged
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable += self.__update
            voipMgr.onChannelLost += self.__update
            voipMgr.onJoinedChannel += self.__update
            voipMgr.onLeftChannel += self.__update
        return

    def __unsubscribe(self):
        CommandMapping.g_instance.onMappingChanged -= self._updateMapping
        InputHandler.g_instance.onKeyDown -= self.__handleKeyDown
        InputHandler.g_instance.onKeyUp -= self.__handleKeyUp
        self.__settingsCore.onSettingsChanged -= self._onSettingsChanged
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            voipMgr.onChannelAvailable -= self.__update
            voipMgr.onChannelLost -= self.__update
            voipMgr.onJoinedChannel -= self.__update
            voipMgr.onLeftChannel -= self.__update
        return

    @staticmethod
    def __getKeyBind(cmd):
        return getReadableKey(cmd) if getKey(cmd) != Keys.KEY_NONE else _KEY_NONE_TEXT

    def __update(self, *_, **__):
        component = self.__component()
        if component:
            component.as_setVoiceChatActivatedS(self.isJoined and self.isEnabled)
            component.as_setVoiceChatEnabledS(self.isEnabled)
