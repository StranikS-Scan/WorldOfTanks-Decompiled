# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/common.py
""" AOP classes for altering some common logic according to Bootcamp's requirements.

    This module should only contain aspects which are reusable by different pointcuts,
    and pointcuts which must be active across all Bootcamp states.
"""
from helpers import aop, dependency
from debug_utils import LOG_CURRENT_EXCEPTION
from debug_utils_bootcamp import LOG_ERROR_BOOTCAMP, LOG_DEBUG_DEV_BOOTCAMP
from skeletons.gui.game_control import IBootcampController

def weave(weaver):
    """ Activates all pointcuts which must be active globally in Bootcamp.
    :param weaver: AOP weaver to use for scoping
    """
    weaver.weave(pointcut=_PointcutDisableSettingsControls)


class _PointcutDisableSettingsControls(aop.Pointcut):
    """ Disable some controls in SettingsWindow before as_setDataS issued
    """

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.common.settings.SettingsWindow', 'SettingsWindow', 'as_setDataS', aspects=(_AspectDisableSettingsControls,))


class AspectAvoidAsync(aop.Aspect):
    """ Reusable aspect for blocking calls of functions decorated with @async.
        Also optionally replaces return value (sent to callback at the end of the wrapped function call).
    """

    def __init__(self, ret=None, cbwrapper=lambda x: x):
        """
        :param ret: value to send to callback at the end of the wrapped function call
                    (adisp will return it to the calling function)
        :param cbwrapper: same as cbwrapper arg for @async decorator
        """
        super(AspectAvoidAsync, self).__init__()
        self.__ret = ret
        self.__cbwrapper = cbwrapper

    def atCall(self, cd):
        cd.avoid()
        return lambda callback: self.__cbwrapper(callback)(self.__ret)


class AspectAvoidWithConstantRet(aop.Aspect):
    """ Reusable aspect for blocking calls and replacing their return value with a specified constant. """

    def __init__(self, ret):
        super(AspectAvoidWithConstantRet, self).__init__()
        self.__ret = ret

    def atCall(self, cd):
        cd.avoid()
        return self.__ret


class AspectRedirectMethod(aop.Aspect):
    """ Reusable aspect for optionally redirecting a method call to a provided callable override.
        Original method will not be called if the override returns True.
        Supports redirecting different multiple methods at once by passing a dict to __init__.
    """

    def __init__(self, override):
        """
        :param override: either a single callable to use for the redirect,
                         or a dict mapping method names to callables.
                         In second case, the dict must contain all possible methods.
        """
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
    """ Reusable aspect for disabling GUI sounds. Can be customized for specific control IDs and states. """

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
    """ Disable some controls in SettingsWindow before as_setDataS issued
    """
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def atCall(self, cd):
        LOG_DEBUG_DEV_BOOTCAMP('Disabling controls in settings window')
        for disableItem in self.bootcampCtrl.getDisabledSettings():
            self.__disableControl(cd, disableItem)

    def __disableControl(self, cd, controlPath):
        """
        :param cd: passed from aspect
        :param controlPath: path to control in Scaleform hierarchy.
            Either page->control or page->subpage->control.
            So, controlPath accordingly contains 2 or 3 items:
            [page, control] or [page, subpage, control]
        :return: None
        """
        page = ''
        subpage = ''
        control = ''
        if len(controlPath) == 2:
            page, control = controlPath
        elif len(controlPath) == 3:
            page, subpage, control = controlPath
        try:
            cd.self.as_disableControlS(page, control, subpage)
        except:
            LOG_ERROR_BOOTCAMP('Error: No such page or control?', page, subpage, control)
            LOG_CURRENT_EXCEPTION()
