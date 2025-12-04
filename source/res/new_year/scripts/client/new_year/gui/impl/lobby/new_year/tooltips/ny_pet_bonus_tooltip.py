# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_pet_bonus_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from helpers import dependency
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_pet_bonus_tooltip_model import NyPetBonusTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from new_year.ny_constants import PERCENT
from new_year.skeletons.new_year import INewYearController, ITamagotchiDataProvider
if typing.TYPE_CHECKING:
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel

class NyPetBonusTooltip(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self, petViewModel):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyPetBonusTooltip())
        settings.model = NyPetBonusTooltipModel()
        self.__fillModel(settings.model)
        self.__fillIndicators(settings.model, petViewModel)
        super(NyPetBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyPetBonusTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self._dataProvider.onSimulationEnd, self.__updateBonus), (self._dataProvider.onBonusUpdated, self.__updateBonus))

    @classmethod
    def __fillModel(cls, model):
        with model.transaction() as tx:
            maxBonus = cls._nyController.getMaxBonusValue() * PERCENT
            constBonus = cls._nyController.getActiveSettingBonusValue() * PERCENT
            dynamicBonus = cls._dataProvider.getDeb()
            tx.setCurrentBonus(constBonus + dynamicBonus)
            tx.setMinBonus(constBonus)
            tx.setMaxBonus(maxBonus)

    @classmethod
    def __fillIndicators(cls, model, petViewModel):
        array = model.getIndicators()
        array.clear()
        array.addViewModel(petViewModel.foodIndicator)
        array.addViewModel(petViewModel.funIndicator)
        array.addViewModel(petViewModel.activityIndicator)
        array.invalidate()

    def __updateBonus(self):
        self.__fillModel(self.viewModel)
