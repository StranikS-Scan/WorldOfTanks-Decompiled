# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/markers/ny_customization_object_marker_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MarkerType(Enum):
    FRIEND = 'friend'
    DEFAULT = 'default'


class NyCustomizationObjectMarkerModel(ViewModel):
    __slots__ = ('onLevelUpdate',)
    MAX_LEVEL = 5

    def __init__(self, properties=7, commands=1):
        super(NyCustomizationObjectMarkerModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getObjectType(self):
        return self._getString(1)

    def setObjectType(self, value):
        self._setString(1, value)

    def getMarkerType(self):
        return MarkerType(self._getString(2))

    def setMarkerType(self, value):
        self._setString(2, value.value)

    def getIsAbleForUpgrade(self):
        return self._getBool(3)

    def setIsAbleForUpgrade(self, value):
        self._setBool(3, value)

    def getIsCameraOnUnderSpace(self):
        return self._getBool(4)

    def setIsCameraOnUnderSpace(self, value):
        self._setBool(4, value)

    def getIsVisible(self):
        return self._getBool(5)

    def setIsVisible(self, value):
        self._setBool(5, value)

    def getIsMaxLevelState(self):
        return self._getBool(6)

    def setIsMaxLevelState(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyCustomizationObjectMarkerModel, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addStringProperty('objectType', '')
        self._addStringProperty('markerType')
        self._addBoolProperty('isAbleForUpgrade', False)
        self._addBoolProperty('isCameraOnUnderSpace', False)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isMaxLevelState', False)
        self.onLevelUpdate = self._addCommand('onLevelUpdate')
