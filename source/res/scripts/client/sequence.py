# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/sequence.py
import BigWorld
import AnimationSequence
from debug_utils import LOG_ERROR
from ids_generators import SequenceIDGenerator
from wotdecorators import condition

class _WrappedSequence(object):

    def __init__(self):
        self.__model = None
        self.__animator = None
        return

    def init(self, path, spaceID, matrix, visible):
        self.__model = model = BigWorld.Model('')
        model.visible = visible
        model.position = matrix.translation
        model.addMotor(BigWorld.Servo(matrix))
        loader = AnimationSequence.Loader(path, spaceID)
        self.__animator = animator = loader.loadSync()
        if not animator:
            LOG_ERROR('Sequence animator not loaded', path)
            return
        animator.bindTo(AnimationSequence.ModelWrapperContainer(model, spaceID))

    def fini(self):
        model = self.__model
        if model.inWorld:
            BigWorld.player().delModel(model)
            self.__model = None
        animator = self.__animator
        if animator:
            animator.halt()
            self.__animator = None
        return

    def play(self, loopCount, speed):
        if not self.__animator:
            return
        self.__model.visible = True
        self.__animator.loopCount = loopCount
        self.__animator.speed = speed
        self.__animator.start()

    def matrix(self):
        return self.__model.matrix

    def setMatrix(self, matrix):
        self.__model.position = matrix.translation
        self.__model.addMotor(BigWorld.Servo(matrix))


class SequenceManager(object):
    _idGen = SequenceIDGenerator()
    _ifEnabled = condition('isEnabled')

    def __init__(self):
        self.__enabled = False
        self._sequences = {}
        self._spaceID = None
        return

    @property
    def isEnabled(self):
        return self.__enabled

    def init(self, spaceID):
        self.__enabled = True
        self._spaceID = spaceID

    def destroy(self):
        for sequence in self._sequences.values():
            sequence.fini()

        self._sequences.clear()
        self.__enabled = False

    @_ifEnabled
    def createSequence(self, path, matrix, visible):
        sequence = _WrappedSequence()
        sequence.init(path, self._spaceID, matrix, visible)
        nextID = self._idGen.next()
        self._sequences[nextID] = sequence
        return nextID

    @_ifEnabled
    def deleteSequence(self, seqID):
        sequence = self._sequences.pop(seqID, None)
        if sequence is None:
            LOG_ERROR('Sequence not found', seqID)
            return
        else:
            sequence.fini()
            return

    @_ifEnabled
    def playSequence(self, seqID, loopCount, speed):
        if not self.__checkSequenceExist(seqID):
            return
        self._sequences[seqID].play(loopCount, speed)

    @_ifEnabled
    def sequenceMatrix(self, seqID):
        return None if not self.__checkSequenceExist(seqID) else self._sequences[seqID].matrix()

    @_ifEnabled
    def setSequenceMatrix(self, seqID, matrix):
        return None if not self.__checkSequenceExist(seqID) else self._sequences[seqID].setMatrix(matrix)

    def __checkSequenceExist(self, seqID):
        if seqID not in self._sequences:
            LOG_ERROR('Sequence not found', seqID)
            return False
        return True
