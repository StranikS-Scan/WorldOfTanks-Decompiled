# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintCustom.py
import BigWorld
from HintsBase import HintBase, HINT_COMMAND

class HintCustom(HintBase):
    __ACTION_NONE = 0
    __ACTION_SHOW = 1
    __ACTION_HIDE = 2
    __ACTION_COMPLETE = 3
    __ACTION_DISABLE = 4

    def __init__(self, avatar, hintId, timeCompleted, cooldownAfter, message, startDelay, duration, innerCooldown, completeDuration, voiceover=None):
        super(HintCustom, self).__init__(avatar, hintId, 0.0)
        self.__action = HintCustom.__ACTION_NONE
        self.timeCompleted = timeCompleted
        self.cooldownAfter = cooldownAfter
        self.message = message
        self.voiceover = voiceover
        self.__timeStartDelay = startDelay
        self.__timeDuration = duration
        self.__timeInnerCooldown = innerCooldown
        self.__timeCompleteDuration = completeDuration
        self.__actionTime = 0.0
        self.__shouldAutoShow = False
        self.__wasntVisible = True
        self.__queueDisabling = False

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self.__actionTime = 0.0
        self.__shouldAutoShow = False
        self.__wasntVisible = True
        self.__queueDisabling = False

    def stop(self):
        self._state = HintBase.STATE_INACTIVE

    def show(self):
        if self._state == HintBase.STATE_HINT or self._state == HintBase.STATE_INACTIVE:
            return
        self.__actionTime = BigWorld.time() + self.__timeStartDelay
        self.__action = HintCustom.__ACTION_SHOW

    def hide(self):
        if self._state == HintBase.STATE_INACTIVE:
            return
        self.__actionTime = BigWorld.time()
        self.__action = HintCustom.__ACTION_HIDE
        self.__shouldAutoShow = False

    def complete(self):
        if self._state == HintBase.STATE_INACTIVE:
            return
        self.__actionTime = BigWorld.time()
        self.__action = HintCustom.__ACTION_COMPLETE

    def disable(self):
        if self._state == HintBase.STATE_INACTIVE:
            return
        if self._state == HintBase.STATE_HINT or self.__action == HintCustom.__ACTION_SHOW or self.__action == HintCustom.__ACTION_COMPLETE:
            self.__queueDisabling = True
        else:
            self._state = HintBase.STATE_INACTIVE

    def update(self):
        if self._state == HintBase.STATE_INACTIVE:
            return None
        else:
            if BigWorld.time() >= self.__actionTime:
                if self.__action == HintCustom.__ACTION_SHOW:
                    if self.__timeDuration > 0.0:
                        self.__actionTime = BigWorld.time() + self.__timeDuration
                        self.__action = HintCustom.__ACTION_HIDE
                        if self.__timeInnerCooldown > 0.0 and not self.__queueDisabling:
                            self.__shouldAutoShow = True
                        else:
                            self.__shouldAutoShow = False
                    else:
                        self.__action = HintCustom.__ACTION_NONE
                    if self._state == HintBase.STATE_DEFAULT:
                        self._state = HintBase.STATE_HINT
                        self.__wasntVisible = False
                        return HINT_COMMAND.SHOW
                elif self.__action == HintCustom.__ACTION_HIDE:
                    if self.__shouldAutoShow and self.__timeInnerCooldown > 0.0:
                        self.__actionTime = BigWorld.time() + self.__timeInnerCooldown
                        self.__action = HintCustom.__ACTION_SHOW
                    else:
                        self.__action = HintCustom.__ACTION_NONE
                    if self._state == HintBase.STATE_HINT or self._state == HintBase.STATE_COMPLETE:
                        if self.__queueDisabling:
                            self._state = HintBase.STATE_INACTIVE
                        elif self.__shouldAutoShow:
                            self._state = HintBase.STATE_DEFAULT
                        else:
                            self._state = HintBase.STATE_DEFAULT
                        return HINT_COMMAND.HIDE
                elif self.__action == HintCustom.__ACTION_COMPLETE:
                    self.__action = HintCustom.__ACTION_HIDE
                    self.__actionTime = BigWorld.time() + self.__timeCompleteDuration
                    self.__shouldAutoShow = False
                    self._state = HintBase.STATE_COMPLETE
                    return HINT_COMMAND.SHOW_COMPLETED
            return None

    def isVisible(self):
        return self._state == HintBase.STATE_HINT

    def isActive(self):
        return self.__action == HintCustom.__ACTION_SHOW or self._state == HintBase.STATE_HINT

    def isNotShown(self):
        return self.__wasntVisible and self.__action != HintCustom.__ACTION_SHOW

    def isComplete(self):
        return self._state == HintBase.STATE_COMPLETE

    def isDisabled(self):
        return self._state == HintBase.STATE_INACTIVE
