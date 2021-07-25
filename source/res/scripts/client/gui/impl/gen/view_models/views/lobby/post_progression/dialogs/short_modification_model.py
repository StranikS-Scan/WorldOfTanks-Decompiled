# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/dialogs/short_modification_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ModificationType(Enum):
    MODIFICATION = 'modification'
    PAIRMODIFICATION = 'pairModification'
    MODIFICATIONWITHFEATURE = 'modificationWithFeature'


class ShortModificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ShortModificationModel, self).__init__(properties=properties, commands=commands)

    def getModificationName(self):
        return self._getString(0)

    def setModificationName(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getModificationType(self):
        return self._getString(2)

    def setModificationType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ShortModificationModel, self)._initialize()
        self._addStringProperty('modificationName', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('modificationType', '')
