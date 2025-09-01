# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/base_ammunition_slot.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class BaseAmmunitionSlot(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
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

    def getImageName(self):
        return self._getString(4)

    def setImageName(self, value):
        self._setString(4, value)

    def getIconName(self):
        return self._getString(5)

    def setIconName(self, value):
        self._setString(5, value)

    def getWithAttention(self):
        return self._getBool(6)

    def setWithAttention(self, value):
        self._setBool(6, value)

    def getIsInstalled(self):
        return self._getBool(7)

    def setIsInstalled(self, value):
        self._setBool(7, value)

    def getIsMountedMoreThanOne(self):
        return self._getBool(8)

    def setIsMountedMoreThanOne(self, value):
        self._setBool(8, value)

    def getItemInstalledSetupIdx(self):
        return self._getNumber(9)

    def setItemInstalledSetupIdx(self, value):
        self._setNumber(9, value)

    def getOverlayType(self):
        return self._getString(10)

    def setOverlayType(self, value):
        self._setString(10, value)

    def getHighlightType(self):
        return self._getString(11)

    def setHighlightType(self, value):
        self._setString(11, value)

    def getCategoryImgSource(self):
        return self._getResource(12)

    def setCategoryImgSource(self, value):
        self._setResource(12, value)

    def _initialize(self):
        super(BaseAmmunitionSlot, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('keyName', '')
        self._addResourceProperty('imageSource', R.invalid())
        self._addStringProperty('imageName', '')
        self._addStringProperty('iconName', '')
        self._addBoolProperty('withAttention', False)
        self._addBoolProperty('isInstalled', True)
        self._addBoolProperty('isMountedMoreThanOne', False)
        self._addNumberProperty('itemInstalledSetupIdx', -1)
        self._addStringProperty('overlayType', '')
        self._addStringProperty('highlightType', '')
        self._addResourceProperty('categoryImgSource', R.invalid())
