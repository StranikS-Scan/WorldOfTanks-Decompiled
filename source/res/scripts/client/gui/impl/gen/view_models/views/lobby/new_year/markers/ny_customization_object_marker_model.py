# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/markers/ny_customization_object_marker_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MarkerType(Enum):
    FRIEND = 'friend'
    DEFAULT = 'default'


class NyCustomizationObjectMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
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

    def getIsUpgradable(self):
        return self._getBool(3)

    def setIsUpgradable(self, value):
        self._setBool(3, value)

    def getIsAbleForUpgrade(self):
        return self._getBool(4)

    def setIsAbleForUpgrade(self, value):
        self._setBool(4, value)

    def getIsCameraOnUnderSpace(self):
        return self._getBool(5)

    def setIsCameraOnUnderSpace(self, value):
        self._setBool(5, value)

    def getTutorialState(self):
        return self._getNumber(6)

    def setTutorialState(self, value):
        self._setNumber(6, value)

    def getIsVisible(self):
        return self._getBool(7)

    def setIsVisible(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NyCustomizationObjectMarkerModel, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addStringProperty('objectType', '')
        self._addStringProperty('markerType')
        self._addBoolProperty('isUpgradable', False)
        self._addBoolProperty('isAbleForUpgrade', False)
        self._addBoolProperty('isCameraOnUnderSpace', False)
        self._addNumberProperty('tutorialState', 0)
        self._addBoolProperty('isVisible', True)
