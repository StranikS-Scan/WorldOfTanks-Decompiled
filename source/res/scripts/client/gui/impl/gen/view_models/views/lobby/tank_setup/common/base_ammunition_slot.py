# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/base_ammunition_slot.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BaseAmmunitionSlot(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(BaseAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIntCD(self):
        return self._getNumber(1)

    def setIntCD(self, value):
        self._setNumber(1, value)

    def getKeyName(self):
        return self._getString(2)

    def setKeyName(self, value):
        self._setString(2, value)

    def getImageSource(self):
        return self._getResource(3)

    def setImageSource(self, value):
        self._setResource(3, value)

    def getWithAttention(self):
        return self._getBool(4)

    def setWithAttention(self, value):
        self._setBool(4, value)

    def getIsInstalled(self):
        return self._getBool(5)

    def setIsInstalled(self, value):
        self._setBool(5, value)

    def getOverlayType(self):
        return self._getString(6)

    def setOverlayType(self, value):
        self._setString(6, value)

    def getHighlightType(self):
        return self._getString(7)

    def setHighlightType(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(BaseAmmunitionSlot, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('keyName', '')
        self._addResourceProperty('imageSource', R.invalid())
        self._addBoolProperty('withAttention', False)
        self._addBoolProperty('isInstalled', True)
        self._addStringProperty('overlayType', '')
        self._addStringProperty('highlightType', '')
