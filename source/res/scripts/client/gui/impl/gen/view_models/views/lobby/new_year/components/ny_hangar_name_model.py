# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_hangar_name_model.py
from frameworks.wulf import ViewModel

class NyHangarNameModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyHangarNameModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getNumber(0)

    def setTitle(self, value):
        self._setNumber(0, value)

    def getDescription(self):
        return self._getNumber(1)

    def setDescription(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyHangarNameModel, self)._initialize()
        self._addNumberProperty('title', 0)
        self._addNumberProperty('description', 0)
