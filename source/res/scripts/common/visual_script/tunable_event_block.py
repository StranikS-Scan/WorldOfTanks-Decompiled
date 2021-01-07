# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/tunable_event_block.py
import BigWorld
from functools import wraps
from block import Block
from slot_types import SLOT_TYPE

class TunableEventBlock(Block):
    _EVENT_SLOT_NAMES = ['onEvent']

    def __init__(self, *args, **kwargs):
        super(TunableEventBlock, self).__init__(*args, **kwargs)
        self.__out = []
        for name in self._EVENT_SLOT_NAMES:
            self.__out.append(self._makeEventOutputSlot(name))

        self._active = self._makeDataInputSlot('active', SLOT_TYPE.BOOL)
        self._maxCount = self._makeDataInputSlot('maxCount', SLOT_TYPE.INT)
        self._cooldown = self._makeDataInputSlot('cooldown', SLOT_TYPE.FLOAT)
        count = len(self._EVENT_SLOT_NAMES)
        self.__lastCallTime = [-1000000] * count
        self.__currentCount = [0] * count
        self._index = 0

    def _isReady(self):
        i = self._index
        return False if self._active.hasValue() and not self._active.getValue() or self._cooldown.hasValue() and BigWorld.time() - self.__lastCallTime[i] < self._cooldown.getValue() or self._maxCount.hasValue() and self.__currentCount[i] >= self._maxCount.getValue() else True

    def _push(self):
        self.__lastCallTime[self._index] = BigWorld.time()
        self.__currentCount[self._index] += 1
        self.__out[self._index].call()

    @staticmethod
    def eventProcessor(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._isReady():
                func(self, *args, **kwargs)
                self._push()

        return wrapper

    def validate(self):
        pass
