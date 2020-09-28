# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/event_task_model.py
from frameworks.wulf import ViewModel

class EventTaskModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EventTaskModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getQuantity(self):
        return self._getNumber(1)

    def setQuantity(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(EventTaskModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('quantity', 0)
