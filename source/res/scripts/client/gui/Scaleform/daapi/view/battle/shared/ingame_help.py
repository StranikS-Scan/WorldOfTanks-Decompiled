# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ingame_help.py
import Keys
from account_helpers.settings_core.settings_constants import CONTROLS, GRAPHICS
from gui.Scaleform.daapi.view.meta.IngameDetailsHelpWindowMeta import IngameDetailsHelpWindowMeta
from gui.Scaleform.daapi.view.meta.IngameHelpWindowMeta import IngameHelpWindowMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.genConsts.KEYBOARD_KEYS import KEYBOARD_KEYS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.ingame_help import detailed_help_pages
from gui.shared import event_dispatcher
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
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
 KEYBOARD_KEYS.HIGHLIGHT_LOCATION,
 KEYBOARD_KEYS.HIGHLIGHT_TARGET,
 KEYBOARD_KEYS.PUSH_TO_TALK,
 KEYBOARD_KEYS.SHOW_HUD)
_FIXED_KEYS_IN_HELP = ((KEYBOARD_KEYS.TOGGLE_PLAYER_PANEL_MODES, Keys.KEY_TAB), (KEYBOARD_KEYS.SHOW_EX_PLAYER_INFO, Keys.KEY_LALT))

def getChangedKeysInfo(settingsCore):
    setting = settingsCore.options.getSetting(CONTROLS.KEYBOARD)
    getter = setting.getSetting
    for key in _CHANGED_KEYS_IN_HELP:
        yield (key, getter(key).get())


def getFixedKeysInfo():
    for key, code in _FIXED_KEYS_IN_HELP:
        yield (key, getScaleformKey(code))


class IngameHelpWindow(IngameHelpWindowMeta, BattleGUIKeyHandler):
    settingsCore = dependency.descriptor(ISettingsCore)

    def onWindowClose(self):
        self.destroy()

    def onWindowMinimize(self):
        self.destroy()

    def handleEscKey(self, isDown):
        return isDown

    def clickSettingWindow(self):
        self.destroy()
        event_dispatcher.showSettingsWindow(redefinedKeyMode=True, tabIndex=event_dispatcher.SettingsTabIndex.CONTROL, isBattleSettings=True)

    def _populate(self):
        super(IngameHelpWindow, self)._populate()
        self.as_setColorBlindS(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
        vo = dict(((key, value) for key, value in getChangedKeysInfo(self.settingsCore)))
        vo.update(dict(((key, value) for key, value in getFixedKeysInfo())))
        self.as_setKeysS(vo)
        return

    def _dispose(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
        super(IngameHelpWindow, self)._dispose()
        return


class IngameDetailsHelpWindow(IngameDetailsHelpWindowMeta, BattleGUIKeyHandler):

    def __init__(self, ctx=None):
        super(IngameDetailsHelpWindow, self).__init__()
        self.__ctx = ctx

    def onWindowClose(self):
        self.destroy()

    def onWindowMinimize(self):
        self.destroy()

    def handleEscKey(self, isDown):
        return isDown

    def _populate(self):
        super(IngameDetailsHelpWindow, self)._populate()
        if self.__ctx is None:
            return
        else:
            self.__detailedList, selectedIdx = detailed_help_pages.buildPagesData(self.__ctx)
            if self.app is not None:
                self.app.registerGuiKeyHandler(self)
                if len(self.__detailedList) > 1:
                    self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.HELP_DETAILED, cursorVisible=True, enableAiming=False)
            pages = [ {'buttonsGroup': 'DetailsHelpPageGroup',
             'pageIndex': index,
             'label': str(index + 1),
             'status': '',
             'selected': index == selectedIdx,
             'tooltip': {}} for index in range(len(self.__detailedList)) ]
            self.as_setPaginatorDataS(pages)
            return

    def requestPageData(self, index):
        self.as_setPageDataS(self.__detailedList[index])

    def _dispose(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.HELP_DETAILED)
        super(IngameDetailsHelpWindow, self)._dispose()
        return
