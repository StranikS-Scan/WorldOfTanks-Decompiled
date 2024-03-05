# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/queue_view/queue_view_model.py
from frameworks.wulf import ViewModel

class QueueViewModel(ViewModel):
    __slots__ = ('onLeave',)

    def __init__(self, properties=1, commands=1):
        super(QueueViewModel, self).__init__(properties=properties, commands=commands)

    def getPlayersInQueue(self):
        return self._getNumber(0)

    def setPlayersInQueue(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(QueueViewModel, self)._initialize()
        self._addNumberProperty('playersInQueue', 0)
        self.onLeave = self._addCommand('onLeave')
