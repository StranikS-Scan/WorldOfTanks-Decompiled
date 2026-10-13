# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/serial_enter_tab_view_model.py
from frameworks.wulf import ViewModel

class SerialEnterTabViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SerialEnterTabViewModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getIsViewed(self):
        return self._getBool(2)

    def setIsViewed(self, value):
        self._setBool(2, value)

    def getIsFinal(self):
        return self._getBool(3)

    def setIsFinal(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SerialEnterTabViewModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isViewed', False)
        self._addBoolProperty('isFinal', False)
