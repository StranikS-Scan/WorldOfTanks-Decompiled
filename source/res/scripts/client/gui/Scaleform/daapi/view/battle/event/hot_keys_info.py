# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/hot_keys_info.py
import Keys
from account_helpers.settings_core.settings_constants import CONTROLS
from gui.Scaleform.daapi.view.meta.EventHotKeysInfoMeta import EventHotKeysInfoMeta
from gui.shared.utils.key_mapping import getScaleformKey
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class EventHotKeysInfo(EventHotKeysInfoMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EventHotKeysInfo, self).__init__()
        self.__keyboardSettings = self.settingsCore.options.getSetting(CONTROLS.KEYBOARD)

    def _populate(self):
        super(EventHotKeysInfo, self)._populate()
        self.__keyboardSettings.onKeyBindingsChanged += self.__updateKeys
        self.__updateKeys()

    def _dispose(self):
        self.__keyboardSettings.onKeyBindingsChanged -= self.__updateKeys
        super(EventHotKeysInfo, self)._dispose()

    def __updateKeys(self):
        keysMap = self.__keyboardSettings.get()
        targetKey = keysMap.get('my_target/follow_me', getScaleformKey(Keys.KEY_T))
        self.as_setButtonsS(targetKey, getScaleformKey(Keys.KEY_TAB))
