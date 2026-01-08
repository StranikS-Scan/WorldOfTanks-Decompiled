# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/pet_storage_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.pet_system.pet_bonus_model import PetBonusModel
from gui.impl.gen.view_models.views.lobby.pet_system.pet_card_model import PetCardModel
from gui.impl.gen.view_models.views.lobby.pet_system.pet_name_model import PetNameModel
from gui.impl.gen.view_models.views.lobby.pet_system.promotion_model import PromotionModel

class SynergyStateEnum(Enum):
    INCOMPLETE = 'incomplete'
    UPDATEDRECENTLY = 'updatedRecently'
    COMPLETE = 'complete'


class VisibilityStateEnum(IntEnum):
    ALWAYS = 0
    DISABLEANIMATION = 1
    ONLYINTOPETPLACE = 2


class PetStorageViewModel(ViewModel):
    __slots__ = ('onClose', 'onBonusSelect', 'onPetSelect', 'onCardSelect', 'onInfoPageOpen', 'onSaveVisibility', 'onSaveName', 'onCloseNameSelection')

    def __init__(self, properties=18, commands=8):
        super(PetStorageViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def promotionModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getPromotionModelType():
        return PromotionModel

    def getPetID(self):
        return self._getNumber(1)

    def setPetID(self, value):
        self._setNumber(1, value)

    def getActivePetID(self):
        return self._getNumber(2)

    def setActivePetID(self, value):
        self._setNumber(2, value)

    def getPetNameID(self):
        return self._getNumber(3)

    def setPetNameID(self, value):
        self._setNumber(3, value)

    def getPetType(self):
        return self._getString(4)

    def setPetType(self, value):
        self._setString(4, value)

    def getBreedName(self):
        return self._getString(5)

    def setBreedName(self, value):
        self._setString(5, value)

    def getSynergyState(self):
        return SynergyStateEnum(self._getString(6))

    def setSynergyState(self, value):
        self._setString(6, value.value)

    def getTotalCount(self):
        return self._getNumber(7)

    def setTotalCount(self, value):
        self._setNumber(7, value)

    def getCurrentCount(self):
        return self._getNumber(8)

    def setCurrentCount(self, value):
        self._setNumber(8, value)

    def getBonuses(self):
        return self._getArray(9)

    def setBonuses(self, value):
        self._setArray(9, value)

    @staticmethod
    def getBonusesType():
        return PetBonusModel

    def getSelectedBonus(self):
        return self._getNumber(10)

    def setSelectedBonus(self, value):
        self._setNumber(10, value)

    def getIsPetSelected(self):
        return self._getBool(11)

    def setIsPetSelected(self, value):
        self._setBool(11, value)

    def getCards(self):
        return self._getArray(12)

    def setCards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getCardsType():
        return PetCardModel

    def getPetNames(self):
        return self._getArray(13)

    def setPetNames(self, value):
        self._setArray(13, value)

    @staticmethod
    def getPetNamesType():
        return PetNameModel

    def getVisibilityState(self):
        return VisibilityStateEnum(self._getNumber(14))

    def setVisibilityState(self, value):
        self._setNumber(14, value.value)

    def getHasUniqueName(self):
        return self._getBool(15)

    def setHasUniqueName(self, value):
        self._setBool(15, value)

    def getHasNewNames(self):
        return self._getBool(16)

    def setHasNewNames(self, value):
        self._setBool(16, value)

    def getIsUnsuitableMode(self):
        return self._getBool(17)

    def setIsUnsuitableMode(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(PetStorageViewModel, self)._initialize()
        self._addViewModelProperty('promotionModel', PromotionModel())
        self._addNumberProperty('petID', 0)
        self._addNumberProperty('activePetID', 0)
        self._addNumberProperty('petNameID', 0)
        self._addStringProperty('petType', '')
        self._addStringProperty('breedName', '')
        self._addStringProperty('SynergyState')
        self._addNumberProperty('totalCount', 0)
        self._addNumberProperty('currentCount', 0)
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('selectedBonus', 0)
        self._addBoolProperty('isPetSelected', False)
        self._addArrayProperty('cards', Array())
        self._addArrayProperty('petNames', Array())
        self._addNumberProperty('visibilityState')
        self._addBoolProperty('hasUniqueName', False)
        self._addBoolProperty('hasNewNames', False)
        self._addBoolProperty('isUnsuitableMode', False)
        self.onClose = self._addCommand('onClose')
        self.onBonusSelect = self._addCommand('onBonusSelect')
        self.onPetSelect = self._addCommand('onPetSelect')
        self.onCardSelect = self._addCommand('onCardSelect')
        self.onInfoPageOpen = self._addCommand('onInfoPageOpen')
        self.onSaveVisibility = self._addCommand('onSaveVisibility')
        self.onSaveName = self._addCommand('onSaveName')
        self.onCloseNameSelection = self._addCommand('onCloseNameSelection')
