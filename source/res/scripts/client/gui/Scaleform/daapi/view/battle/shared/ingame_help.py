# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ingame_help.py
import Keys
from account_helpers.settings_core import g_settingsCore
from account_helpers.settings_core.settings_constants import CONTROLS
from gui.Scaleform.daapi.view.meta.IngameHelpWindowMeta import IngameHelpWindowMeta
from gui.Scaleform.genConsts.KEYBOARD_KEYS import KEYBOARD_KEYS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.shared import event_dispatcher
from gui.shared.utils.key_mapping import getScaleformKey
_CHANGED_KEYS_IN_HELP = (KEYBOARD_KEYS.FORWARD,
 KEYBOARD_KEYS.BACKWARD,
 KEYBOARD_KEYS.LEFT,
 KEYBOARD_KEYS.RIGHT,
 KEYBOARD_KEYS.AUTO_ROTATION,
 KEYBOARD_KEYS.FORWARD_CRUISE,
 KEYBOARD_KEYS.BACKWARD_CRUISE,
 KEYBOARD_KEYS.FIRE,
 KEYBOARD_KEYS.LOCK_TARGET,
 KEYBOARD_KEYS.LOCK_TARGET_OFF,
 KEYBOARD_KEYS.ALTERNATE_MODE,
 KEYBOARD_KEYS.RELOAD_PARTIAL_CLIP,
 KEYBOARD_KEYS.STOP_FIRE,
 KEYBOARD_KEYS.SHOW_RADIAL_MENU,
 KEYBOARD_KEYS.ATTACK,
 KEYBOARD_KEYS.PUSH_TO_TALK,
 KEYBOARD_KEYS.SHOW_HUD)
_FIXED_KEYS_IN_HELP = ((KEYBOARD_KEYS.TOGGLE_PLAYER_PANEL_MODES, Keys.KEY_TAB), (KEYBOARD_KEYS.SHOW_EX_PLAYER_INFO, Keys.KEY_LALT))

def getChangedKeysInfo():
    setting = g_settingsCore.options.getSetting(CONTROLS.KEYBOARD)
    getter = setting.getSetting
    for key in _CHANGED_KEYS_IN_HELP:
        yield (key, getter(key).get())


def getFixedKeysInfo():
    for key, code in _FIXED_KEYS_IN_HELP:
        yield (key, getScaleformKey(code))


class IngameHelpWindow(IngameHelpWindowMeta, BattleGUIKeyHandler):

    def onWindowClose(self):
        self.destroy()

    def onWindowMinimize(self):
        self.destroy()

    def handleEscKey(self, isDown):
        return isDown

    def clickSettingWindow(self):
        self.destroy()
        event_dispatcher.showSettingsWindow(redefinedKeyMode=True, tabIndex=event_dispatcher.SETTINGS_TAB_INDEX.CONTROL)

    def _populate(self):
        super(IngameHelpWindow, self)._populate()
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
        vo = dict(((key, value) for key, value in getChangedKeysInfo()))
        vo.update(dict(((key, value) for key, value in getFixedKeysInfo())))
        self.as_setKeysS(vo)
        return

    def _dispose(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        super(IngameHelpWindow, self)._dispose()
        return
