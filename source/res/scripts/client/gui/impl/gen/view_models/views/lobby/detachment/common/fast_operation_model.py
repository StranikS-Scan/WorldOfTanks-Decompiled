# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/fast_operation_model.py
from frameworks.wulf import ViewModel

class FastOperationModel(ViewModel):
    __slots__ = ('onRetrainClick', 'onPreviousClick', 'onTopClick', 'onDropInBarrackClick')

    def __init__(self, properties=4, commands=4):
        super(FastOperationModel, self).__init__(properties=properties, commands=commands)

    def getRetrainState(self):
        return self._getString(0)

    def setRetrainState(self, value):
        self._setString(0, value)

    def getPreviousState(self):
        return self._getString(1)

    def setPreviousState(self, value):
        self._setString(1, value)

    def getTopState(self):
        return self._getString(2)

    def setTopState(self, value):
        self._setString(2, value)

    def getDropInBarrackState(self):
        return self._getString(3)

    def setDropInBarrackState(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(FastOperationModel, self)._initialize()
        self._addStringProperty('retrainState', '')
        self._addStringProperty('previousState', '')
        self._addStringProperty('topState', '')
        self._addStringProperty('dropInBarrackState', '')
        self.onRetrainClick = self._addCommand('onRetrainClick')
        self.onPreviousClick = self._addCommand('onPreviousClick')
        self.onTopClick = self._addCommand('onTopClick')
        self.onDropInBarrackClick = self._addCommand('onDropInBarrackClick')
