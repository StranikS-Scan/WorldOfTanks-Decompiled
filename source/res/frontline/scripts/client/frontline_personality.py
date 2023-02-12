# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline_personality.py
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from frontline_common.constants import ACCOUNT_DEFAULT_SETTINGS
from constants import ARENA_GUI_TYPE, PREBATTLE_TYPE, QUEUE_TYPE, ARENA_BONUS_TYPE
from constants_utils import AbstractBattleMode
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
LOBBY_EXT_PACKAGES = ['frontline.gui.Scaleform.daapi.view.lobby', 'frontline.gui.Scaleform.daapi.view.lobby.hangar']

class ClientFrontlineBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.EPIC
    _QUEUE_TYPE = QUEUE_TYPE.EPIC
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.EPIC_BATTLE
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.EPIC_BATTLE
    _CLIENT_PRB_ACTION_NAME = PREBATTLE_ACTION_NAME.EPIC
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = EPICBATTLES_ALIASES.EPIC_BATTLES_ENTRY_POINT

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        from frontline.gui.Scaleform.daapi.view.lobby.hangar.entry_point import isEpicBattlesEntryPointAvailable
        return isEpicBattlesEntryPointAvailable


def preInit():
    battleMode = ClientFrontlineBattleMode(__name__)
    battleMode.registerBannerEntryPointValidatorMethod()


def init():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    g_overrideScaleFormViewsConfig.initExtensionLobbyPackages(__name__, LOBBY_EXT_PACKAGES)


def start():
    pass


def fini():
    pass
