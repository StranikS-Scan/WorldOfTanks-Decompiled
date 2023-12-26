# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/markers/ny_resource_marker_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AnimationState(Enum):
    DISABLED = 'disabled'
    AVAILABLE = 'available'
    COLLECTING = 'collecting'


class MarkerType(Enum):
    FRIEND = 'friend'
    DEFAULT = 'default'


class NyResourceMarkerModel(ViewModel):
    __slots__ = ('onAnimationEnd',)

    def __init__(self, properties=5, commands=1):
        super(NyResourceMarkerModel, self).__init__(properties=properties, commands=commands)

    def getResourceType(self):
        return self._getString(0)

    def setResourceType(self, value):
        self._setString(0, value)

    def getCollectAmount(self):
        return self._getNumber(1)

    def setCollectAmount(self, value):
        self._setNumber(1, value)

    def getAnimationState(self):
        return AnimationState(self._getString(2))

    def setAnimationState(self, value):
        self._setString(2, value.value)

    def getMarkerType(self):
        return MarkerType(self._getString(3))

    def setMarkerType(self, value):
        self._setString(3, value.value)

    def getIsVisible(self):
        return self._getBool(4)

    def setIsVisible(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NyResourceMarkerModel, self)._initialize()
        self._addStringProperty('resourceType', '')
        self._addNumberProperty('collectAmount', 0)
        self._addStringProperty('animationState')
        self._addStringProperty('markerType')
        self._addBoolProperty('isVisible', True)
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
