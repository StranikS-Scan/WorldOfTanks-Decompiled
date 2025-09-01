# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/assembling_video_view_model.py
from frameworks.wulf import ViewModel

class AssemblingVideoViewModel(ViewModel):
    __slots__ = ('startAssembling',)

    def __init__(self, properties=2, commands=1):
        super(AssemblingVideoViewModel, self).__init__(properties=properties, commands=commands)

    def getOperationID(self):
        return self._getNumber(0)

    def setOperationID(self, value):
        self._setNumber(0, value)

    def getStageNumber(self):
        return self._getNumber(1)

    def setStageNumber(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(AssemblingVideoViewModel, self)._initialize()
        self._addNumberProperty('operationID', 0)
        self._addNumberProperty('stageNumber', 0)
        self.startAssembling = self._addCommand('startAssembling')
