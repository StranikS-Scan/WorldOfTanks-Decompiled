# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/summary/dog_tag_model.py
from frameworks.wulf import ViewModel

class DogTagModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(DogTagModel, self).__init__(properties=properties, commands=commands)

    def getEngravingCompId(self):
        return self._getNumber(0)

    def setEngravingCompId(self, value):
        self._setNumber(0, value)

    def getBackgroundCompId(self):
        return self._getNumber(1)

    def setBackgroundCompId(self, value):
        self._setNumber(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getIsHighlighted(self):
        return self._getBool(3)

    def setIsHighlighted(self, value):
        self._setBool(3, value)

    def getBackground(self):
        return self._getString(4)

    def setBackground(self, value):
        self._setString(4, value)

    def getEngraving(self):
        return self._getString(5)

    def setEngraving(self, value):
        self._setString(5, value)

    def getPurpose(self):
        return self._getString(6)

    def setPurpose(self, value):
        self._setString(6, value)

    def getAnimation(self):
        return self._getString(7)

    def setAnimation(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(DogTagModel, self)._initialize()
        self._addNumberProperty('engravingCompId', 0)
        self._addNumberProperty('backgroundCompId', 0)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isHighlighted', False)
        self._addStringProperty('background', '')
        self._addStringProperty('engraving', '')
        self._addStringProperty('purpose', '')
        self._addStringProperty('animation', '')
