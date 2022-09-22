# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_settings/aop.py
from helpers import aop, dependency
from skeletons.gui.game_control import IEventSettingsController

class PointcutDisableSettingsControls(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.common.settings.SettingsWindow', 'SettingsWindow', 'as_setDataS', aspects=(_AspectDisableSettingsControls,))


class _AspectDisableSettingsControls(aop.Aspect):
    __eventSettingsController = dependency.descriptor(IEventSettingsController)

    def atCall(self, cd):
        for disableItem in self.__eventSettingsController.disabledSettings:
            self.__disableControl(cd, disableItem)

    def atReturn(self, cd):
        cd.self.updateIsEvent()

    def __disableControl(self, cd, controlPath):
        page = ''
        subpage = ''
        control = ''
        if len(controlPath) == 2:
            page, control = controlPath
        elif len(controlPath) == 3:
            page, subpage, control = controlPath
        cd.self.as_disableControlS(page, control, subpage)
