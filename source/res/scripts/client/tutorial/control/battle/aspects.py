# Embedded file name: scripts/client/tutorial/control/battle/aspects.py
import weakref
from helpers import aop

class AmmoQuantityAspect(aop.Aspect):

    def __init__(self, trigger):
        super(AmmoQuantityAspect, self).__init__()
        self.__triggerRef = weakref.ref(trigger)

    def atCall(self, cd):
        trigger = self.__triggerRef()
        if trigger is None:
            return
        else:
            trigger.toggle(isOn=trigger.isOn(shoot=True))
            return

    def clear(self):
        self.__triggerRef = None
        return


class CameraZoomModeIgnoreAspect(aop.Aspect):

    def atCall(self, cd):
        function = cd.function.__name__
        args = list(cd.args)
        kwargs = cd.kwargs
        if function == 'restoreDefaultsState':
            cd.avoid()
        else:
            if len(args) > 5:
                args[-2] = False
            else:
                kwargs['zoomMode'] = False
            cd.change()
        return (args, kwargs)


class MouseScrollIgnoreAspect(aop.Aspect):

    def atCall(self, cd):
        args = list(cd.args)
        if args[2] != 0.0:
            args[2] = 0.0
            cd.change()
        return (args, cd.kwargs)


class AmmoQuantityPointcut(aop.Pointcut):

    def __init__(self):
        super(AmmoQuantityPointcut, self).__init__('Avatar', 'Avatar', '^shoot$')


class AltModeTogglePointcut(aop.Pointcut):

    def __init__(self):
        super(AltModeTogglePointcut, self).__init__('AvatarInputHandler.control_modes', 'ArcadeControlMode', '^_ArcadeControlMode__activateAlternateMode$')


class CameraUpdatePointcut(aop.Pointcut):

    def __init__(self):
        super(CameraUpdatePointcut, self).__init__('AvatarInputHandler.DynamicCameras.ArcadeCamera', 'ArcadeCamera', '^restoreDefaultsState|_ArcadeCamera__update$')


class ArcadeCtrlMouseEventsPointcut(aop.Pointcut):

    def __init__(self):
        super(ArcadeCtrlMouseEventsPointcut, self).__init__('AvatarInputHandler.control_modes', 'ArcadeControlMode', '^handleMouseEvent')
