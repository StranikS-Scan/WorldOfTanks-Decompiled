# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_map_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MapsTrainingMapModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(MapsTrainingMapModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getImage(self):
        return self._getResource(2)

    def setImage(self, value):
        self._setResource(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getIsCompleted(self):
        return self._getBool(4)

    def setIsCompleted(self, value):
        self._setBool(4, value)

    def getGroupId(self):
        return self._getNumber(5)

    def setGroupId(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(MapsTrainingMapModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('image', R.invalid())
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('groupId', 0)
