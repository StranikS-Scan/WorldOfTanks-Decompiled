# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/new_maps_model.py
from frameworks.wulf import ViewModel

class NewMapsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NewMapsModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(NewMapsModel, self)._initialize()
        self._addStringProperty('name', '')
