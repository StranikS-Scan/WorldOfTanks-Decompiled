# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsLobby.py
import time
import math
from copy import copy
from bootcamp.BootcampConstants import HINT_TYPE
from HintsBase import HintBase, HINT_COMMAND
from AvatarInputHandler import mathUtils
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class HintLobbyRotate(HintBase):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, params):
        super(HintLobbyRotate, self).__init__(None, HINT_TYPE.HINT_ROTATE_LOBBY, params['timeout'])
        self.__prevCameraDirection = None
        self.__neededAngle = math.radians(params['angle'])
        self.__curAngle = 0.0
        self.__cancelAngle = params.get('cancelAngle', 0.2)
        return

    def update(self):
        if self._state == HintBase.STATE_INACTIVE or self._state == HintBase.STATE_COMPLETE:
            return
        elif self.hangarSpace is None or self.hangarSpace.space is None:
            return
        else:
            camera = self.hangarSpace.space.camera
            if camera is None:
                return
            elif self.__prevCameraDirection is None:
                self.__prevCameraDirection = copy(camera.direction)
                self.__prevCameraDirection.normalise()
                return
            curDirection = copy(camera.direction)
            curDirection.normalise()
            cosAngle = self.__prevCameraDirection.dot(curDirection)
            cosAngle = mathUtils.clamp(-1.0, 1.0, cosAngle)
            self.__curAngle += abs(math.acos(cosAngle))
            self.__prevCameraDirection = curDirection
            resultCommand = None
            if self._state == HintBase.STATE_HINT:
                if self.__curAngle > self.__neededAngle:
                    self._state = HintBase.STATE_COMPLETE
                    resultCommand = HINT_COMMAND.SHOW_COMPLETED_WITH_HINT
            elif self._state == HintBase.STATE_DEFAULT:
                if time.time() - self._timeStart > self._timeout:
                    self._state = HintBase.STATE_HINT
                    resultCommand = HINT_COMMAND.SHOW
                elif self.__curAngle > self.__cancelAngle:
                    self._state = HintBase.STATE_COMPLETE
                    resultCommand = HINT_COMMAND.SHOW_COMPLETED
            return resultCommand

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self._timeStart = time.time()

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
