# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline_personality.py
from account_helpers.AccountSettings import AccountSettings, KEY_SETTINGS
from frontline_common.constants import ACCOUNT_DEFAULT_SETTINGS
from constants import ARENA_GUI_TYPE
from frontline.gui.Scaleform.daapi.view.lobby.hangar.entry_point import addFrontlineEntryPoint
from gui.override_scaleform_views_manager import g_overrideScaleFormViewsConfig
LOBBY_EXT_PACKAGES = ('frontline.gui.Scaleform.daapi.view.lobby', 'frontline.gui.Scaleform.daapi.view.lobby.hangar')
BATTLE_EXT_PACKAGES = {}

def preInit():
    pass


def init():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    g_overrideScaleFormViewsConfig.initExtensionGUIPackages(__name__, LOBBY_EXT_PACKAGES, BATTLE_EXT_PACKAGES, ARENA_GUI_TYPE.EPIC_BATTLE)
    addFrontlineEntryPoint()


def start():
    pass


def fini():
    pass
