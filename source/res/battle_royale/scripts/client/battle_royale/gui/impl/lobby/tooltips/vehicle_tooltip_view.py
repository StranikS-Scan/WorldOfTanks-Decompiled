# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/vehicle_tooltip_view.py
from __future__ import absolute_import
import typing
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_tooltip_view_model import VehicleTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.doc_loaders.battle_royale_settings_loader import getVehicleProperties
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.tooltips.vehicle import StatusBlockConstructor
from gui.shared.tooltips.contexts import InventoryContext
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from battle_royale.gui.impl.lobby.br_helpers.utils import setEventInfo
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale.gui.impl.gen.view_models.views.lobby.enums import CoinType
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class VehicleTooltipView(ViewImpl):
    __brController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, intCD):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.vehicle())
        settings.model = VehicleTooltipViewModel()
        self.__context = InventoryContext()
        self.__vehicle = self.__context.buildItem(intCD)
        super(VehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleTooltipView, self)._onLoading(args, kwargs)
        with self.getViewModel().transaction() as model:
            self.__fillStats(model.tech)
            self.__fillModel(model)

    def __fillStats(self, model):
        if br_helpers.isIncorrectVehicle(self.__vehicle):
            return
        nationName = self.__vehicle.nationName
        params = getVehicleProperties(nationName)
        model.setSpotting(params.spotting)
        model.setDifficulty(params.difficulty)
        model.setSurvivability(params.survivability)
        model.setMobility(params.mobility)
        model.setDamage(params.damage)

    def __fillModel(self, model):
        setEventInfo(model.eventInfo)
        model.setVehicleName(self.__vehicle.userName)
        model.setVehicleNation(self.__vehicle.nationName)
        model.setVehicleType(self.__vehicle.type)
        self.__fillStatus(self.__vehicle, model)
        modeSettings = self.__brController.getModeSettings()
        model.dailyBonus.setHasDailyBonus(self.__brController.hasDailyBonus(self.__vehicle))
        model.dailyBonus.setDailyBonusFactor(modeSettings.dailyBonus.get('bonusFactor', 0))
        model.dailyBonus.setSoloTopPlaces(modeSettings.dailyBonus.get('soloTopPlaces', 0))
        model.dailyBonus.setSquadTopPlaces(modeSettings.dailyBonus.get('squadTopPlaces', 0))
        model.dailyBonus.setCoinType(CoinType.STPCOIN)

    def __fillStatus(self, vehicle, model):
        statusConfig = self.__context.getStatusConfiguration(vehicle)
        _, __, status = StatusBlockConstructor(vehicle, statusConfig).construct()
        model.setStatusText(status['header'])
        model.setStatusLevel(status['level'])
