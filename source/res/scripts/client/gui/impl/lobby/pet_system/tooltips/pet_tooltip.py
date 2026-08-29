# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/tooltips/pet_tooltip.py
import logging
from frameworks.wulf import ViewSettings, Array
from frameworks.wulf.view.array import fillStringsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.tooltips.pet_tooltip_model import PetTooltipModel
from gui.impl.pub import ViewImpl
from gui.pet_system.pet_item_helper import PromoPetItem
from gui.pet_system.requester import INVALID_PET_ID
_logger = logging.getLogger(__name__)

class PetTooltip(ViewImpl):

    def __init__(self, petID=INVALID_PET_ID, *args, **kwargs):
        settings = ViewSettings(R.views.mono.pet_system.tooltips.pet_tooltip())
        settings.model = PetTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.petID = petID
        super(PetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PetTooltip, self)._onLoading(*args, **kwargs)
        if self.petID == INVALID_PET_ID:
            _logger.warning('petID is invalid')
            return
        bonusesStrList = PromoPetItem.getPetBenefits(self.petID)
        bonuses = Array()
        fillStringsArray(bonusesStrList, bonuses)
        with self.viewModel.transaction() as model:
            model.setPetID(self.petID)
            model.setPetNameID(PromoPetItem.getDefaultNameId(self.petID))
            model.setPetType(PromoPetItem.getPetType(self.petID))
            model.setBreedName(PromoPetItem.getPetBreed(self.petID))
            model.setPromotionBonuses(bonuses)
