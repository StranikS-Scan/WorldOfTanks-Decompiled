# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_video_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from sound_gui_manager import CommonSoundSpaceSettings
_SOUND_STATE_INFOPAGE = 'STATE_infopage_show'
_SOUND_STATE_INFOPAGE_ON = 'STATE_infopage_show_on'
_SOUND_STATE_INFOPAGE_OFF = 'STATE_infopage_show_off'

class BattlePassVideoBrowserView(WebView):
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=_SOUND_STATE_INFOPAGE, entranceStates={_SOUND_STATE_INFOPAGE: _SOUND_STATE_INFOPAGE_ON}, exitStates={_SOUND_STATE_INFOPAGE: _SOUND_STATE_INFOPAGE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

    def _dispose(self):
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.VIDEO_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
        super(BattlePassVideoBrowserView, self)._dispose()
