# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/settings/white_tiger_settings_controller.py
from __future__ import absolute_import
from helpers import dependency
from account_helpers.settings_core.settings_disable.disable_settings_ctrl import DisableSettingsController
from white_tiger.gui.game_control.settings.aop import PointcutDisableSettingsControls
from white_tiger.gui.game_control.settings.white_tiger_disabled_settings import WhiteTigerDisabledSettings
from white_tiger.gui.game_control.settings.white_tiger_override_settings import WhiteTigerOverrideSettings
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class WhiteTigerSettingsController(DisableSettingsController):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        super(WhiteTigerSettingsController, self).__init__()
        self.__disabledSettings = None
        self.__overrideSettings = None
        return

    def init(self):
        super(WhiteTigerSettingsController, self).init()
        self.__disabledSettings = WhiteTigerDisabledSettings()
        self.__overrideSettings = WhiteTigerOverrideSettings()
        settings = self.__overrideSettings.overrideSettings
        for optionName, data in settings.items():
            if isinstance(data, dict):
                group = optionName
                if len(data) <= 0:
                    continue
                firstOption = next(iter(data))
                storage = self.__overrideSettings.getStorageName(firstOption)
                self.registerRecord(name=group, value=data, storages=(storage,), guiPath=[], disable=False)
                continue
            storage = self.__overrideSettings.getStorageName(optionName)
            self.registerRecord(name=optionName, value=data, storages=(storage,), guiPath=[], disable=False)

    def fini(self):
        self.__disabledSettings = None
        self.__overrideSettings = None
        return

    def _canBeApplied(self):
        return self.__wtController.isInWhiteTigerMode()

    def _disable(self):
        super(WhiteTigerSettingsController, self)._disable()
        if self._weaver.findPointcut(PointcutDisableSettingsControls) == -1:
            self._weaver.weave(pointcut=PointcutDisableSettingsControls)

    @property
    def disabledSettings(self):
        return self.__disabledSettings.disabledSetting
