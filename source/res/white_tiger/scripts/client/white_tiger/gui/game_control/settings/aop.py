# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/settings/aop.py
from helpers import aop, dependency
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class PointcutDisableSettingsControls(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.common.settings.SettingsWindow', 'SettingsWindow', 'as_setDataS')
        self.addAspect(_AspectDisableSettingsControls)


class _AspectDisableSettingsControls(aop.Aspect):
    __whiteTigerController = dependency.descriptor(IWhiteTigerController)

    def atCall(self, cd):
        disabledSettings = self.__whiteTigerController.getDisabledSettings()
        for disableItem in disabledSettings:
            self.__disableControl(cd, disableItem)

    def __disableControl(self, cd, controlPath):
        page = ''
        subpage = ''
        control = ''
        if len(controlPath) == 2:
            page, control = controlPath
        elif len(controlPath) == 3:
            page, subpage, control = controlPath
        cd.self.as_disableControlS(page, control, subpage)
