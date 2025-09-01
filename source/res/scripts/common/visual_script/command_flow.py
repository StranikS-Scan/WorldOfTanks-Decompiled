# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/command_flow.py
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE

class _CommandFlowMeta(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return ASPECT.ALL


class MutexGate(Block, _CommandFlowMeta):

    def __init__(self, *args, **kwargs):
        super(MutexGate, self).__init__(*args, **kwargs)
        self._input = self._makeEventInputSlot('in', self.tryActivate)
        self._lockSlot = self._makeEventInputSlot('lock', self.lock)
        self._releaseSlot = self._makeEventInputSlot('release', self.release)
        self._lockedAtStart = self._makeDataInputSlot('lockedAtStart', SLOT_TYPE.BOOL)
        self._outSlot = self._makeEventOutputSlot('out')
        self._isLocked = False
        self._isReady = False

    def onStartScript(self):
        self._isLocked = self._lockedAtStart.getValue()

    def lock(self):
        self._isLocked = False

    def tryActivate(self):
        if self._isLocked:
            self._outSlot.call()
        else:
            self._isReady = True

    def release(self):
        if self._isReady:
            self._outSlot.call()
        self._isReady = False
