# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/base_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class BaseSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(BaseSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIntCD(self):
        return self._getNumber(2)

    def setIntCD(self, value):
        self._setNumber(2, value)

    def getImageName(self):
        return self._getString(3)

    def setImageName(self, value):
        self._setString(3, value)

    def getItemsInStorage(self):
        return self._getNumber(4)

    def setItemsInStorage(self, value):
        self._setNumber(4, value)

    def getItemTypeID(self):
        return self._getNumber(5)

    def setItemTypeID(self, value):
        self._setNumber(5, value)

    def getIsMounted(self):
        return self._getBool(6)

    def setIsMounted(self, value):
        self._setBool(6, value)

    def getIsDisabled(self):
        return self._getBool(7)

    def setIsDisabled(self, value):
        self._setBool(7, value)

    def getIsVisible(self):
        return self._getBool(8)

    def setIsVisible(self, value):
        self._setBool(8, value)

    def getInstalledSlotId(self):
        return self._getNumber(9)

    def setInstalledSlotId(self, value):
        self._setNumber(9, value)

    def getIsLocked(self):
        return self._getBool(10)

    def setIsLocked(self, value):
        self._setBool(10, value)

    def getOverlayType(self):
        return self._getString(11)

    def setOverlayType(self, value):
        self._setString(11, value)

    def getHighlightType(self):
        return self._getString(12)

    def setHighlightType(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(BaseSlotModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addStringProperty('name', '')
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('imageName', '')
        self._addNumberProperty('itemsInStorage', 0)
        self._addNumberProperty('itemTypeID', 0)
        self._addBoolProperty('isMounted', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isVisible', True)
        self._addNumberProperty('installedSlotId', -1)
        self._addBoolProperty('isLocked', False)
        self._addStringProperty('overlayType', '')
        self._addStringProperty('highlightType', '')
