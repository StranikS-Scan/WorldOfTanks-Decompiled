# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ingame_help.py
import Keys
import CommandMapping
from account_helpers.settings_core.settings_constants import CONTROLS
from gui.Scaleform.daapi.view.meta.IngameHelpWindowMeta import IngameHelpWindowMeta
from gui.Scaleform.daapi.view.meta.IngameDetailsHelpWindowMeta import IngameDetailsHelpWindowMeta
from gui.Scaleform.genConsts.KEYBOARD_KEYS import KEYBOARD_KEYS
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.Scaleform.locale.INGAME_HELP import INGAME_HELP
from gui.shared import event_dispatcher
from gui.shared.utils.key_mapping import getScaleformKey, getReadableKey
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
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
        event_dispatcher.showSettingsWindow(redefinedKeyMode=True, tabIndex=event_dispatcher.SETTINGS_TAB_INDEX.CONTROL, isBattleSettings=True)

    def _populate(self):
        super(IngameHelpWindow, self)._populate()
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

    @staticmethod
    def __addPage(datailedList, title, descr, buttons, image):
        data = {'title': title,
         'descr': descr,
         'buttons': buttons,
         'image': image}
        datailedList.append(data)

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
        if self.app is not None:
            self.app.registerGuiKeyHandler(self)
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.HELP_DETAILED, cursorVisible=True, enableAiming=False)
        if self.__ctx is None:
            return
        else:
            self.__datailedList = list()
            if self.__ctx.get('hasSiegeMode'):
                siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
                keyName = siegeKeyName if siegeKeyName else _ms(INGAME_HELP.DETAILSHELP_NOKEY)
                self.__addPage(self.__datailedList, INGAME_HELP.DETAILSHELP_TWOMODES_TITLE, _ms(INGAME_HELP.DETAILSHELP_TWOMODES, key1=keyName), [siegeKeyName], RES_ICONS.MAPS_ICONS_BATTLEHELP_WHEEL_TWO_MODE)
            if self.__ctx.get('hasBurnout'):
                breakeKeyName = getReadableKey(CommandMapping.CMD_BLOCK_TRACKS)
                forwardKeyName = getReadableKey(CommandMapping.CMD_MOVE_FORWARD)
                keyName1 = breakeKeyName if breakeKeyName else _ms(INGAME_HELP.DETAILSHELP_NOKEY)
                keyName2 = forwardKeyName if forwardKeyName else _ms(INGAME_HELP.DETAILSHELP_NOKEY)
                self.__addPage(self.__datailedList, INGAME_HELP.DETAILSHELP_BURNOUT_TITLE, _ms(INGAME_HELP.DETAILSHELP_BURNOUT, key1=keyName1, key2=keyName2), [forwardKeyName, breakeKeyName], RES_ICONS.MAPS_ICONS_BATTLEHELP_WHEEL_BURNOUT)
            if self.__ctx.get('isWheeled'):
                self.__addPage(self.__datailedList, INGAME_HELP.DETAILSHELP_STABLECHASSIS_TITLE, _ms(INGAME_HELP.DETAILSHELP_STABLECHASSIS), [], RES_ICONS.MAPS_ICONS_BATTLEHELP_WHEEL_CHASSIS)
                self.__addPage(self.__datailedList, INGAME_HELP.DETAILSHELP_ABOUTTECHNIQUE_TITLE, _ms(INGAME_HELP.DETAILSHELP_ABOUTTECHNIQUE), [], RES_ICONS.MAPS_ICONS_BATTLEHELP_WHEEL_DETAILS)
            pages = [ {'buttonsGroup': 'DetailsHelpPageGroup',
             'pageIndex': index,
             'label': str(index + 1),
             'status': '',
             'selected': index == 0,
             'tooltip': {}} for index in range(0, len(self.__datailedList)) ]
            self.as_setInitDataS({'pages': pages,
             'title': self.__ctx.get('name')})
            return

    def requestHelpData(self, index):
        data = self.__datailedList[index]
        self.as_setHelpDataS(data)

    def _dispose(self):
        if self.app is not None:
            self.app.unregisterGuiKeyHandler(self)
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.HELP_DETAILED)
        super(IngameDetailsHelpWindow, self)._dispose()
        return
