# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/common.py
from helpers import aop, dependency
from debug_utils import LOG_CURRENT_EXCEPTION
from debug_utils_bootcamp import LOG_ERROR_BOOTCAMP, LOG_DEBUG_DEV_BOOTCAMP
from skeletons.gui.game_control import IBootcampController

def weave(weaver):
    weaver.weave(pointcut=_PointcutDisableSettingsControls)
    weaver.weave(pointcut=_PointcutHideMinimapNames)
    weaver.weave(pointcut=_PointcutLimitNotificationPopUpsCount)


class _PointcutDisableSettingsControls(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.common.settings.SettingsWindow', 'SettingsWindow', 'as_setDataS', aspects=(_AspectDisableSettingsControls,))


class _PointcutHideMinimapNames(aop.Pointcut):

    def __init__(self):
        super(_PointcutHideMinimapNames, self).__init__('gui.Scaleform.daapi.view.battle.shared.minimap.common', 'SimplePlugin', '_invoke', aspects=(_AspectHideMinimapNames,))


class _PointcutLimitNotificationPopUpsCount(aop.Pointcut):

    def __init__(self):
        super(_PointcutLimitNotificationPopUpsCount, self).__init__('notification.NotificationPopUpViewer', 'NotificationPopUpViewer', '_getSettings', aspects=(_AspectLimitNotificationPopUpsCount,))


class AspectAvoidAsync(aop.Aspect):

    def __init__(self, ret=None, cbwrapper=lambda x: x):
        super(AspectAvoidAsync, self).__init__()
        self.__ret = ret
        self.__cbwrapper = cbwrapper

    def atCall(self, cd):
        cd.avoid()
        return lambda callback: self.__cbwrapper(callback)(self.__ret)


class AspectAvoidWithConstantRet(aop.Aspect):

    def __init__(self, ret):
        super(AspectAvoidWithConstantRet, self).__init__()
        self.__ret = ret

    def atCall(self, cd):
        cd.avoid()
        return self.__ret


class AspectRedirectMethod(aop.Aspect):

    def __init__(self, override):
        super(AspectRedirectMethod, self).__init__()
        self.__override = override

    def atCall(self, cd):
        if isinstance(self.__override, dict):
            f = self.__override[cd.function.__name__]
        else:
            f = self.__override
        if f(*cd.args, **cd.kwargs):
            cd.avoid()


class AspectDisableControlSound(aop.Aspect):

    def __init__(self, disabledStates, disabledIDs):
        super(AspectDisableControlSound, self).__init__()
        self.__disabledStates = disabledStates
        self.__disabledIDs = disabledIDs

    def atCall(self, cd):
        state = cd.args[0]
        id = cd.args[2]
        if state in self.__disabledStates and id in self.__disabledIDs:
            cd.avoid()


class _AspectDisableSettingsControls(aop.Aspect):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def atCall(self, cd):
        LOG_DEBUG_DEV_BOOTCAMP('Disabling controls in settings window')
        for disableItem in self.bootcampCtrl.getDisabledSettings():
            self.__disableControl(cd, disableItem)

    def __disableControl(self, cd, controlPath):
        page = ''
        subpage = ''
        control = ''
        if len(controlPath) == 2:
            page, control = controlPath
        elif len(controlPath) == 3:
            page, subpage, control = controlPath
        try:
            cd.self.as_disableControlS(page, control, subpage)
        except Exception:
            LOG_ERROR_BOOTCAMP('Error: No such page or control?', page, subpage, control)
            LOG_CURRENT_EXCEPTION()


class _AspectHideMinimapNames(aop.Aspect):

    def atCall(self, cd):
        name = cd.findArg(1, '')
        return cd.changeArgs((4, 'arg', '')) if name == 'setVehicleInfo' else None


class _AspectLimitNotificationPopUpsCount(aop.Aspect):

    def atReturn(self, cd):
        cd.change()
        return cd.returned._replace(stackLength=1)
