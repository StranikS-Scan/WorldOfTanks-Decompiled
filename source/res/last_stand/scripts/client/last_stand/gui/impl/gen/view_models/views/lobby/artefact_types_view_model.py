# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/artefact_types_view_model.py
from frameworks.wulf import ViewModel

class ArtefactTypesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ArtefactTypesViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIndex(self):
        return self._getNumber(1)

    def setIndex(self, value):
        self._setNumber(1, value)

    def getTypes(self):
        return self._getString(2)

    def setTypes(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ArtefactTypesViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('index', 0)
        self._addStringProperty('types', '')
