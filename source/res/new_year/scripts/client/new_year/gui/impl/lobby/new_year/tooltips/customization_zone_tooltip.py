# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/customization_zone_tooltip.py
from frameworks.wulf import ViewSettings
from gui.server_events.bonuses import getNonQuestBonuses
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.customization_zone_tooltip_model import CustomizationZoneTooltipModel
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.helpers.server_settings import getNewYearObjectsConfig
from new_year_common.items.components.ny_constants import OBJECT_MAX_LEVEL
from new_year.helpers.ny_helpers import getCurrentObjectLevel
from NewYearBonusesClient import ToyBonus
from new_year.skeletons.new_year import INewYearCurrencyController

class CustomizationZoneTooltip(ViewImpl):
    __slots__ = ('__customizationZone', '__config')
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    def __init__(self, customizationZone):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.CustomizationZoneTooltip())
        settings.model = CustomizationZoneTooltipModel()
        super(CustomizationZoneTooltip, self).__init__(settings)
        self.__customizationZone = customizationZone
        self.__config = getNewYearObjectsConfig()

    @property
    def viewModel(self):
        return super(CustomizationZoneTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__updateModelImpl()

    def __updateModelImpl(self):
        with self.getViewModel().transaction() as model:
            bonusToys = []
            currentLevel = getCurrentObjectLevel(self.__customizationZone)
            toysCount = len(NewYearAtmospherePresenter.getNewYearLevelToys(self.__customizationZone, currentLevel + 1))
            for key, value in self.__config.getBonusForLevel(self.__customizationZone, currentLevel + 1).items():
                bonuses = getNonQuestBonuses(key, value)
                for bonus in bonuses:
                    if isinstance(bonus, ToyBonus):
                        bonusToys.append(bonus)

            model.setCurrentLevel(currentLevel)
            model.setMaxLevel(OBJECT_MAX_LEVEL)
            atmosphereCount = NewYearAtmospherePresenter.getNewYearLevelAtmospherePoints(self.__customizationZone, currentLevel + 1)
            upgradeCost = self.__config.getNextLevelPrice(self.__customizationZone, currentLevel)
            isEnoughValue = self.__nyCurrencyController.getMandarinTokenCount >= upgradeCost
            model.setIsEnoughValue(isEnoughValue)
            model.setAtmosphereCount(atmosphereCount)
            model.setNextLevelDecorations(toysCount)
            model.setUpgradeCost(upgradeCost)
            model.customizationZone.setValue(CustomizationZone(self.__customizationZone))
