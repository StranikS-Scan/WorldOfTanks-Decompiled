# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/sequence.py
import BigWorld
import Math
from visual_script.block import Block, Meta, SLOT_TYPE, ASPECT
from visual_script_client.dependency import dependencyImporter
Avatar = dependencyImporter('Avatar')

class Sequence(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @property
    def manager(self):
        player = BigWorld.player()
        return player if isinstance(player, Avatar.PlayerAvatar) else player.hangarSpace.sequenceManager


class CreateSequence(Block, Sequence):

    def __init__(self, *args, **kwargs):
        super(CreateSequence, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', CreateSequence._onIn)
        self._path = self._makeDataInputSlot('path', SLOT_TYPE.STR)
        self._visible = self._makeDataInputSlot('visible', SLOT_TYPE.BOOL)
        self._matrix = self._makeDataInputSlot('matrix', SLOT_TYPE.MATRIX4)
        self._out = self._makeEventOutputSlot('out')
        self._sequenceID = self._makeDataOutputSlot('sequenceID', SLOT_TYPE.INT, None)
        return

    def _onIn(self):
        seqID = self.manager.createSequence(self._path.getValue(), self._matrix.getValue(), self._visible.getValue())
        self._sequenceID.setValue(seqID)
        self._out.call()


class PlaySequence(Block, Sequence):

    def __init__(self, *args, **kwargs):
        super(PlaySequence, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', PlaySequence._onIn)
        self._sequenceID = self._makeDataInputSlot('sequenceID', SLOT_TYPE.INT)
        self._loop = self._makeDataInputSlot('loop', SLOT_TYPE.BOOL)
        self._loopCount = self._makeDataInputSlot('loopCount', SLOT_TYPE.INT)
        self._speed = self._makeDataInputSlot('speed', SLOT_TYPE.FLOAT)
        self._out = self._makeEventOutputSlot('out')

    def _onIn(self):
        loopCount = self._loopCount.getValue() if self._loop.getValue() else 1
        self.manager.playSequence(self._sequenceID.getValue(), loopCount, self._speed.getValue())
        self._out.call()


class DeleteSequence(Block, Sequence):

    def __init__(self, *args, **kwargs):
        super(DeleteSequence, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', DeleteSequence._onIn)
        self._sequenceID = self._makeDataInputSlot('sequenceID', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')

    def _onIn(self):
        sequenceID = self._sequenceID.getValue()
        self.manager.deleteSequence(sequenceID)
        self._out.call()


class GetSequenceMatrix(Block, Sequence):

    def __init__(self, *args, **kwargs):
        super(GetSequenceMatrix, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', GetSequenceMatrix._onIn)
        self._sequenceID = self._makeDataInputSlot('sequenceID', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')
        self._matrix = self._makeDataOutputSlot('matrix', SLOT_TYPE.MATRIX4, None)
        return

    def _onIn(self):
        sequenceID = self._sequenceID.getValue()
        self._matrix.setValue(self.manager.sequenceMatrix(sequenceID) or Math.Matrix())
        self._out.call()


class SetSequenceMatrix(Block, Sequence):

    def __init__(self, *args, **kwargs):
        super(SetSequenceMatrix, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', SetSequenceMatrix._onIn)
        self._sequenceID = self._makeDataInputSlot('sequenceID', SLOT_TYPE.INT)
        self._matrix = self._makeDataInputSlot('matrix', SLOT_TYPE.MATRIX4)
        self._out = self._makeEventOutputSlot('out')

    def _onIn(self):
        sequenceID = self._sequenceID.getValue()
        self.manager.setSequenceMatrix(sequenceID, self._matrix.getValue())
        self._out.call()
