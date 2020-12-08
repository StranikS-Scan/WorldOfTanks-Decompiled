# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearIciclesIllumination.py
import logging
import AnimationSequence
import BigWorld
from helpers import dependency, newFakeModel
from new_year.ny_icicle_controller import FINAL_ILLUMINATION_ID
from skeletons.new_year import IIcicleController
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

class _AnimationTriggers(object):
    ACTIVATE = 'activate'
    DEACTIVATE = 'deactivate'
    ACTIVATE_INSTANTLY = 'activate_instantly'


class NewYearIciclesIllumination(BigWorld.Entity):
    __icicleController = dependency.descriptor(IIcicleController)

    def __init__(self):
        super(NewYearIciclesIllumination, self).__init__()
        self.__animator = None
        self.__fakeModel = None
        return

    def onEnterWorld(self, prereqs):
        self.__fakeModel = newFakeModel()
        self.__fakeModel.addMotor(BigWorld.Servo(self.matrix))
        BigWorld.addModel(self.__fakeModel)
        if self.stateMachine:
            animationLoader = AnimationSequence.Loader(self.stateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded))
        self.__icicleController.addIlluminationEntity(self)

    def onLeaveWorld(self):
        self.__icicleController.removeIlluminationEntity(self)
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        if self.__fakeModel is not None:
            BigWorld.delModel(self.__fakeModel)
            self.__fakeModel = None
        return

    def activate(self):
        self.__setTrigger(_AnimationTriggers.ACTIVATE)

    def deactivate(self):
        self.__setTrigger(_AnimationTriggers.DEACTIVATE)

    def __onAnimatorLoaded(self, resourceList):
        if self.stateMachine in resourceList.failedIDs:
            _logger.error("Failed to load animation state machine for Icicle's Illumination: [objectID=%s].", self.objectID)
            return
        elif self.__fakeModel is None:
            _logger.error("Failed to setup animation state machine for Icicle's Illumination [objectID=%s]. Model is missing.", self.objectID)
            return
        else:
            self.__animator = resourceList[self.stateMachine]
            self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.__fakeModel, self.spaceID))
            self.__animator.start()
            if self.__icicleController.isCompleted and self.objectID == FINAL_ILLUMINATION_ID:
                self.__setTrigger(_AnimationTriggers.ACTIVATE_INSTANTLY)
            return

    def __setTrigger(self, trigger):
        if self.__animator is not None:
            self.__animator.setTrigger(trigger)
        else:
            _logger.error("Failed to set animation trigger: [trigger=%s] for Icicle's Illumination [objectID-%s]. State machine is missing.", trigger, self.objectID)
        return
