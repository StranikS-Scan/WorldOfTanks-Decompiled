# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_resources_convert_rate.py
from frameworks.wulf import ViewModel

class NyResourcesConvertRate(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyResourcesConvertRate, self).__init__(properties=properties, commands=commands)

    def getFrom(self):
        return self._getNumber(0)

    def setFrom(self, value):
        self._setNumber(0, value)

    def getTo(self):
        return self._getNumber(1)

    def setTo(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyResourcesConvertRate, self)._initialize()
        self._addNumberProperty('from', 0)
        self._addNumberProperty('to', 0)
