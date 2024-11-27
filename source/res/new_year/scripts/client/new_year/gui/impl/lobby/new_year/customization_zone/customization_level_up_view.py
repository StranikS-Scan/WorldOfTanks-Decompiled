# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/customization_zone/customization_level_up_view.py
from adisp import adisp_process
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui import SystemMessages
from frameworks.wulf import ViewSettings
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from new_year.gui.shared.gui_items.processors.ny_processor import UpgradeCustomizationObjectLevel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.customization_zone.customization_level_up_model import CustomizationLevelUpModel
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.helpers.server_settings import getNewYearObjectsConfig
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.helpers.ny_helpers import getCurrentObjectLevel
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter

class CustomizationLevelUpView(ViewImpl):
    __slots__ = ('__customizationZone', '__config', '__currencyProvider')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, customizationZone):
        settings = ViewSettings(R.views.new_year.lobby.new_year.CustomizationLevelUpView())
        settings.model = CustomizationLevelUpModel()
        super(CustomizationLevelUpView, self).__init__(settings)
        self.__customizationZone = customizationZone
        self.__config = getNewYearObjectsConfig()
        self.__currencyProvider = NyCurrencyProvider()

    @property
    def viewModel(self):
        return super(CustomizationLevelUpView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onLevelUp, self.__onLevelUp), (self.viewModel.onClose, self.__onClose))

    def _onLoading(self, *args, **kwargs):
        self.__updateModelImpl()
        NewYearSoundsManager.setHangarFilteredState(True)
        return super(CustomizationLevelUpView, self)._onLoading(*args, **kwargs)

    def __updateModelImpl(self):
        with self.viewModel.transaction() as model:
            currentLevel = getCurrentObjectLevel(self.__customizationZone)
            atmospherePoints = NewYearAtmospherePresenter.getNewYearLevelAtmospherePoints(self.__customizationZone, currentLevel + 1)
            model.setCurrentLevel(currentLevel)
            model.setLevelUpCurrencyNeed(self.__config.getNextLevelPrice(self.__customizationZone, currentLevel))
            model.customizationZone.setValue(CustomizationZone(self.__customizationZone))
            model.setCurrencyCount(self.__currencyProvider.getCurrencyCount(NyCurrencyType.MANDARIN))
            model.setAtmospherePoints(atmospherePoints)

    @adisp_process
    def __onLevelUp(self):
        result = yield UpgradeCustomizationObjectLevel(self.__customizationZone).request()
        SystemMessages.pushMessage(priority=result.msgPriority, text=result.userMsg, type=result.sysMsgType, messageData=result.msgData)
        self.__onClose()

    def __onClose(self):
        self.destroyWindow()
        NewYearSoundsManager.setHangarFilteredState(False)
