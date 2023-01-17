# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from sound_gui_manager import CommonSoundSpaceSettings
from web.web_client_api import sound as sound_web_api, ui as ui_web_api, webApiCollection
from web.web_client_api.battle_pass import BattlePassWebApi
from web.web_client_api.sound import SoundStateWebApi
_SOUND_STATE_INFOPAGE = 'STATE_infopage_show'
_SOUND_STATE_INFOPAGE_ON = 'STATE_infopage_show_on'
_SOUND_STATE_INFOPAGE_OFF = 'STATE_infopage_show_off'

class BattlePassBrowserView(WebView):
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=_SOUND_STATE_INFOPAGE, entranceStates={_SOUND_STATE_INFOPAGE: _SOUND_STATE_INFOPAGE_ON}, exitStates={_SOUND_STATE_INFOPAGE: _SOUND_STATE_INFOPAGE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    __battlePassController = dependency.descriptor(IBattlePassController)

    def webHandlers(self):
        return webApiCollection(BattlePassWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.OpenTabWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi, SoundStateWebApi)

    def _populate(self):
        super(BattlePassBrowserView, self)._populate()
        self.__battlePassController.onBattlePassSettingsChange += self.__onSettingsChange

    def _dispose(self):
        super(BattlePassBrowserView, self)._dispose()
        self.__battlePassController.onBattlePassSettingsChange -= self.__onSettingsChange

    def __onSettingsChange(self, *_):
        if not self.__battlePassController.isVisible() or self.__battlePassController.isPaused():
            self.destroy()
