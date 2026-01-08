# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tooltips/damage_zones_tooltip.py
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.damage_zones_tooltip_model import DamageZonesTooltipModel
from frontline.gui.params import getArmorDamageFactors
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from supply_shared import Supply

class DamageZonesTooltip(ViewImpl):
    __epicMetaController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__supplyName',)

    def __init__(self, layoutID=R.views.frontline.lobby.tooltips.DamageZonesTooltip(), supplyName=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = DamageZonesTooltipModel()
        self.__supplyName = supplyName
        super(DamageZonesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DamageZonesTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DamageZonesTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            config = self.__epicMetaController.getSupplyParams()
            vehicle = Vehicle(typeCompDescr=config[Supply.NAME_TO_SUPPLY[self.__supplyName]]['intCD'])
            hullDamageFactor, turretDamageFactor = getArmorDamageFactors(vehicle.descriptor)
            vm.setSupplyHullDamageFactor(hullDamageFactor)
            vm.setSupplyTurretDamageFactor(turretDamageFactor)
