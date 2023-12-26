# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_customization_object_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_customization_object_tooltip_model import NyCustomizationObjectTooltipModel, ResourceCollectState
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.levelup_price_model import LevelupPriceModel
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from new_year.ny_constants import NYObjects
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_resource_collecting_helper import getAvgResourcesByCollecting, isCollectingAvailable, getCollectingCooldownTime
from skeletons.new_year import INewYearController

class NyCustomizationObjectTooltip(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, objectName):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyCustomizationObjectTooltip())
        settings.model = NyCustomizationObjectTooltipModel()
        self.__objectName = objectName
        super(NyCustomizationObjectTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyCustomizationObjectTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            model.setObjectName(self.__objectName)
            if self.__objectName in NYObjects.UPGRADABLE_GROUP:
                self.__fillAdditionalData(model)
            elif self.__objectName == NYObjects.RESOURCES:
                self.__fillResourceData(model)

    def __fillAdditionalData(self, model):
        currentLevel = self.__nyController.customizationObjects.getLevel(self.__objectName)
        objectsConfig = self.__nyController.customizationObjects.getConfig()
        nextLevelDescr = objectsConfig.getObjectByID(self.__objectName).getNextLevel(currentLevel)
        maxLevel = len(objectsConfig.getObjectByID(self.__objectName).getLevels()) - 1
        model.setCurrentLevel(currentLevel)
        model.setMaxLevel(maxLevel)
        pricesModel = model.price
        pricesModel.clear()
        if nextLevelDescr:
            for currency, count in nextLevelDescr.getLevelPrice().iteritems():
                priceItem = LevelupPriceModel()
                priceItem.setCurrency(currency)
                priceItem.setValue(count)
                pricesModel.addViewModel(priceItem)

        pricesModel.invalidate()

    def __fillResourceData(self, model):
        model.setResourceBaseCollectAmount(getAvgResourcesByCollecting(forceExtraCollect=False))
        model.setResourceExtraCollectAmount(getAvgResourcesByCollecting(forceExtraCollect=True))
        model.setResourceCollectState(self.__getState())

    def __getState(self):
        cooldownTime = getCollectingCooldownTime()
        eventEndTimeTill = getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime()
        if isCollectingAvailable():
            return ResourceCollectState.AVAILABLE
        return ResourceCollectState.FINISHED if cooldownTime > eventEndTimeTill else ResourceCollectState.COLLECTED
