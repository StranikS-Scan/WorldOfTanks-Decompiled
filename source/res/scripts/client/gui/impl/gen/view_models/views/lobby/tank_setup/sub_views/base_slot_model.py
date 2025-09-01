# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/base_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specializations_model import SpecializationsModel

class BaseSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(BaseSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    @property
    def specializations(self):
        return self._getViewModel(1)

    @staticmethod
    def getSpecializationsType():
        return SpecializationsModel

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIntCD(self):
        return self._getNumber(3)

    def setIntCD(self, value):
        self._setNumber(3, value)

    def getImageName(self):
        return self._getString(4)

    def setImageName(self, value):
        self._setString(4, value)

    def getItemsInStorage(self):
        return self._getNumber(5)

    def setItemsInStorage(self, value):
        self._setNumber(5, value)

    def getItemsInVehicle(self):
        return self._getNumber(6)

    def setItemsInVehicle(self, value):
        self._setNumber(6, value)

    def getItemTypeID(self):
        return self._getNumber(7)

    def setItemTypeID(self, value):
        self._setNumber(7, value)

    def getIsMounted(self):
        return self._getBool(8)

    def setIsMounted(self, value):
        self._setBool(8, value)

    def getIsMountedMoreThanOne(self):
        return self._getBool(9)

    def setIsMountedMoreThanOne(self, value):
        self._setBool(9, value)

    def getIsMountedInOtherSetup(self):
        return self._getBool(10)

    def setIsMountedInOtherSetup(self, value):
        self._setBool(10, value)

    def getIsDisabled(self):
        return self._getBool(11)

    def setIsDisabled(self, value):
        self._setBool(11, value)

    def getIsVisible(self):
        return self._getBool(12)

    def setIsVisible(self, value):
        self._setBool(12, value)

    def getInstalledSlotId(self):
        return self._getNumber(13)

    def setInstalledSlotId(self, value):
        self._setNumber(13, value)

    def getItemInstalledSetupIdx(self):
        return self._getNumber(14)

    def setItemInstalledSetupIdx(self, value):
        self._setNumber(14, value)

    def getItemInstalledSetupSlotIdx(self):
        return self._getNumber(15)

    def setItemInstalledSetupSlotIdx(self, value):
        self._setNumber(15, value)

    def getIsLocked(self):
        return self._getBool(16)

    def setIsLocked(self, value):
        self._setBool(16, value)

    def getIsFreeToDemount(self):
        return self._getBool(17)

    def setIsFreeToDemount(self, value):
        self._setBool(17, value)

    def getLockReason(self):
        return self._getString(18)

    def setLockReason(self, value):
        self._setString(18, value)

    def getOverlayType(self):
        return self._getString(19)

    def setOverlayType(self, value):
        self._setString(19, value)

    def getHighlightType(self):
        return self._getString(20)

    def setHighlightType(self, value):
        self._setString(20, value)

    def _initialize(self):
        super(BaseSlotModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('specializations', SpecializationsModel())
        self._addStringProperty('name', '')
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('imageName', '')
        self._addNumberProperty('itemsInStorage', 0)
        self._addNumberProperty('itemsInVehicle', 0)
        self._addNumberProperty('itemTypeID', 0)
        self._addBoolProperty('isMounted', False)
        self._addBoolProperty('isMountedMoreThanOne', False)
        self._addBoolProperty('isMountedInOtherSetup', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isVisible', True)
        self._addNumberProperty('installedSlotId', -1)
        self._addNumberProperty('itemInstalledSetupIdx', -1)
        self._addNumberProperty('itemInstalledSetupSlotIdx', -1)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isFreeToDemount', False)
        self._addStringProperty('lockReason', '')
        self._addStringProperty('overlayType', '')
        self._addStringProperty('highlightType', '')
