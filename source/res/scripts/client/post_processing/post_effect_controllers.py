# Embedded file name: scripts/client/post_processing/post_effect_controllers.py
import BigWorld, Math
import Event
from PostProcessing.Effects import *
from debug_utils import *

class _PostProcessingEvents(object):

    def __init__(self):
        self.onFocalPlaneChanged = Event.Event()


g_postProcessingEvents = _PostProcessingEvents()

class IEffectController(object):

    def __init__(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def create(self):
        pass

    def destroy(self):
        pass


class DofEffectCtrl(IEffectController):

    def __init__(self):
        IEffectController.__init__(self)
        self.__relaxTime = 0.1

    def enable(self):
        g_postProcessingEvents.onFocalPlaneChanged += self.__update

    def disable(self):
        g_postProcessingEvents.onFocalPlaneChanged -= self.__update

    def __update(self):
        from AvatarInputHandler.control_modes import getFocalPoint
        pos = getFocalPoint()
        if pos is None:
            pos = 0
        else:
            pos = (BigWorld.camera().position - pos).length
        farPlane = 1.0 / BigWorld.projection().farPlane
        offset = 2.5
        zNear = (pos - offset) * farPlane
        zFar = (pos + offset) * farPlane
        DepthOfField.zNear.set(zNear, self.__relaxTime, True)
        DepthOfField.zFar.set(zFar, self.__relaxTime, True)
        return


class DofEffectManualDistanceCtrl(IEffectController):
    onDistanceChanged = Event.Event()

    def enable(self):
        DofEffectManualDistanceCtrl.onDistanceChanged += self.__onDistanceChanged

    def disable(self):
        DofEffectManualDistanceCtrl.onDistanceChanged -= self.__onDistanceChanged

    def __onDistanceChanged(self, distance):
        farPlane = 1.0 / BigWorld.projection().farPlane
        offset = 2.5
        zNear = (distance - offset) * farPlane
        zFar = (distance + offset) * farPlane
        DepthOfFieldUnit.zNear.set(zNear, 0.1, True)
        DepthOfFieldUnit.zFar.set(zFar, 0.1, True)
