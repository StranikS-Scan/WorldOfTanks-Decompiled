# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_widget_bonus_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_widget_bonus_tooltip_model import NyWidgetBonusTooltipModel, TooltipState
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from CurrentVehicle import g_currentVehicle
from new_year.ny_bonuses import getBonusStatus
from new_year.ny_level_helper import NewYearAtmospherePresenter
from ny_common.settings import BattleBonusesConsts
from uilogging.ny.loggers import NyMainWidgetTooltipLogger

class NyWidgetBonusTooltip(ViewImpl):
    __slots__ = ('__currentVehicle', '__chosenXPBonus', '__errorStatus')
    _itemsCache = dependency.descriptor(IItemsCache)
    __uiLogger = NyMainWidgetTooltipLogger()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyWidgetBonusTooltip())
        settings.model = NyWidgetBonusTooltipModel()
        self.__currentVehicle = g_currentVehicle.item
        self.__chosenXPBonus = self._itemsCache.items.festivity.getChosenXPBonus()
        self.__errorStatus = getBonusStatus(vehicle=self.__currentVehicle, maxReachedLevel=NewYearAtmospherePresenter.getLevel())
        super(NyWidgetBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyWidgetBonusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        if self.__errorStatus == BattleBonusesConsts.LEVEL_ERROR:
            with self.viewModel.transaction() as tx:
                tx.setLevel(self.__currentVehicle.level)
                tx.setTooltipState(TooltipState.LEVELERROR)
        if self.__errorStatus == BattleBonusesConsts.VEHICLE_ERROR:
            with self.viewModel.transaction() as tx:
                tx.setTooltipState(TooltipState.VEHICLEERROR)
        self.__uiLogger.start()

    def _finalize(self):
        self.__uiLogger.stop(NewYearNavigation.getCurrentObject() is None)
        self.__chosenXPBonus = None
        self.__errorStatus = None
        super(NyWidgetBonusTooltip, self)._finalize()
        return
