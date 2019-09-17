# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_settings/aop.py
from helpers import aop
import event_settings_swapper

class _PointcutDisableSettingsControls(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.common.settings.SettingsWindow', 'SettingsWindow', 'as_setDataS', aspects=(_AspectDisableSettingsControls,))


class _PointcutApplyOnlyUserSettings(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'account_helpers.settings_core.SettingsCore', 'SettingsCore', 'applySettings', aspects=(_AspectApplyOnlyUserSettings,))


class _PointcutApplyUnchangedSettings(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'account_helpers.settings_core.options', 'DynamicCamera', 'apply', aspects=(_AspectApplyUnchanged,))


class _AspectDisableSettingsControls(aop.Aspect):

    def atCall(self, cd):
        for disableItem in event_settings_swapper.g_instance.disabledSettings:
            self.__disableControl(cd, disableItem)

    def atReturn(self, cd):
        cd.self.as_setFestRaceEventS(True)

    def __disableControl(self, cd, controlPath):
        page = ''
        subpage = ''
        control = ''
        if len(controlPath) == 2:
            page, control = controlPath
        elif len(controlPath) == 3:
            page, subpage, control = controlPath
        cd.self.as_disableControlS(page, control, subpage)


class _AspectApplyOnlyUserSettings(aop.Aspect):

    def atCall(self, cd):
        for storage in cd.self._SettingsCore__storages.values():
            storage.clear()


class _AspectApplyUnchanged(aop.Aspect):

    def atCall(self, cd):
        return cd.changeArgs((1, 'applyUnchanged', True))
