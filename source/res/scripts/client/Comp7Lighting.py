# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Comp7Lighting.py
import logging
import AnimationSequence
import BigWorld
from enum import Enum
import math_utils
_logger = logging.getLogger(__name__)

class Comp7LightingTriggers(Enum):
    DEFAULT = 'default_lighting'
    FLYBY = 'purchase_lighting'


class Comp7Lighting(BigWorld.Entity):

    def __init__(self):
        super(Comp7Lighting, self).__init__()
        self.__animator = None
        return

    def prerequisites(self):
        if not self.animationStateMachine:
            _logger.warning('Property animationStateMachine for Comp7Lighting must be set!')
            return ()
        return (AnimationSequence.Loader(self.animationStateMachine, self.spaceID),)

    def onEnterWorld(self, prereqs):
        if self.animationStateMachine in prereqs.failedIDs:
            _logger.warning('Failed to load %s', self.animationStateMachine)
            return
        else:
            self.__animator = prereqs[self.animationStateMachine]
            if self.__animator is None:
                _logger.warning('Loaded None animator for %s', self.animationStateMachine)
                return
            identityMatrix = math_utils.createIdentityMatrix()
            self.__animator.bindToWorld(identityMatrix)
            self.__animator.start()
            return

    def onLeaveWorld(self):
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        return

    def setTrigger(self, triggerName):
        if self.__animator is None:
            _logger.warning('Could not trigger state machine, animator is not loaded')
            return
        else:
            self.__animator.setTrigger(triggerName)
            return
