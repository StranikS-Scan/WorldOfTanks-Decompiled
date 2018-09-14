# Embedded file name: scripts/client/gui/Scaleform/daapi/settings/config.py
from constants import IS_DEVELOPMENT
COMMON_PACKAGES = ('gui.Scaleform.daapi.view.common',)
_LOBBY_RELEASE_PACKAGES = ('gui.Scaleform.daapi.view.lobby', 'gui.Scaleform.daapi.view.lobby.barracks', 'gui.Scaleform.daapi.view.lobby.boosters', 'gui.Scaleform.daapi.view.lobby.clans', 'gui.Scaleform.daapi.view.lobby.crewOperations', 'gui.Scaleform.daapi.view.lobby.customization_2_0', 'gui.Scaleform.daapi.view.lobby.cyberSport', 'gui.Scaleform.daapi.view.lobby.exchange', 'gui.Scaleform.daapi.view.lobby.fortifications', 'gui.Scaleform.daapi.view.lobby.hangar', 'gui.Scaleform.daapi.view.lobby.header', 'gui.Scaleform.daapi.view.lobby.inputChecker', 'gui.Scaleform.daapi.view.lobby.messengerBar', 'gui.Scaleform.daapi.view.lobby.prb_windows', 'gui.Scaleform.daapi.view.lobby.profile', 'gui.Scaleform.daapi.view.lobby.server_events', 'gui.Scaleform.daapi.view.lobby.store', 'gui.Scaleform.daapi.view.lobby.techtree', 'gui.Scaleform.daapi.view.lobby.trainings', 'gui.Scaleform.daapi.view.lobby.wgnc', 'gui.Scaleform.daapi.view.login', 'messenger.gui.Scaleform.view')
_LOBBY_DEBUG_PACKAGES = ('gui.development.ui.GUIEditor', 'gui.development.ui.messenger.view')
_BATTLE_RELEASE_PACKAGES = ()
_BATTLE_DEBUG_PACKAGES = ()
if IS_DEVELOPMENT:
    LOBBY_PACKAGES = _LOBBY_RELEASE_PACKAGES + _LOBBY_DEBUG_PACKAGES
    BATTLE_PACKAGES = _BATTLE_RELEASE_PACKAGES + _BATTLE_DEBUG_PACKAGES
else:
    LOBBY_PACKAGES = _LOBBY_RELEASE_PACKAGES
    BATTLE_PACKAGES = _BATTLE_RELEASE_PACKAGES
