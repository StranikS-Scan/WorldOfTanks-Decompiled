# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/notification_model.py
from frameworks.wulf import ViewModel

class NotificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NotificationModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NotificationModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addStringProperty('type', '')
