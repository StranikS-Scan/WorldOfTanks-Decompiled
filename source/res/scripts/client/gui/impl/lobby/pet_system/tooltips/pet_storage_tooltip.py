# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/tooltips/pet_storage_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.tooltips.pet_storage_tooltip_model import PetStorageTooltipModel
from gui.impl.pub import ViewImpl
from gui.pet_system.bonus_helper import BonusItem
from gui.pet_system.pet_item_helper import PetItem
from helpers import dependency
from skeletons.gui.pet_system import IPetSystemController

class PetStorageTooltip(ViewImpl):
    __petController = dependency.descriptor(IPetSystemController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.pet_system.tooltips.pet_storage_tooltip())
        settings.model = PetStorageTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PetStorageTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PetStorageTooltip, self).getViewModel()

    def _onLoading(self):
        super(PetStorageTooltip, self)._onLoading()
        petID = PetItem.getActivePetID()
        with self.viewModel.transaction() as model:
            model.setPetNameID(PetItem.getCurrentNameId(petID))
            model.setPetType(PetItem.getPetType(petID))
            model.setBreedName(PetItem.getPetBreed(petID))
            model.setPetID(petID)
            model.setIsUnsuitableMode(not self.__petController.checkBonusCapsForPetBonus())
            activeBonusID = BonusItem.getActiveBonus()
            if activeBonusID:
                model.setBonusName(BonusItem.getBonusName(activeBonusID))
                model.setBonusValue(BonusItem.getBonusValue(activeBonusID))
                totalCount = BonusItem.getBonusesPerDay()
                model.setCurrentBattleCount(totalCount - BonusItem.getAppliedBonusCount())
                model.setTotalBattleCount(totalCount)
