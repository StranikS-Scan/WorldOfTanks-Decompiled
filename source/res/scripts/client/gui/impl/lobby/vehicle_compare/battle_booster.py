# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/battle_booster.py
from gui.impl.lobby.tank_setup.array_providers.battle_booster import OptDeviceBattleBoosterProvider, CrewBattleBoosterProvider, EconomicBattleBoosterProvider
from gui.impl.lobby.tank_setup.configurations.battle_booster import BattleBoostersTabsController, BattleBoosterTabs
from gui.impl.lobby.vehicle_compare.base_sub_view import CompareBaseSetupSubView
from gui.shared.utils.requesters import REQ_CRITERIA

class _CompareOptDeviceBattleBoosterProvider(OptDeviceBattleBoosterProvider):

    def _fillBuyPrice(self, *args, **kwargs):
        pass

    def _fillBuyStatus(self, *args, **kwargs):
        pass

    def _getItemCriteria(self):
        return REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT


class _CompareCrewBattleBoosterProvider(CrewBattleBoosterProvider):

    def _fillBuyPrice(self, *args, **kwargs):
        pass

    def _fillBuyStatus(self, *args, **kwargs):
        pass


class _CompareEconomicBattleBoosterProvider(EconomicBattleBoosterProvider):

    def _fillBuyPrice(self, *args, **kwargs):
        pass

    def _fillBuyStatus(self, *args, **kwargs):
        pass

    def _fillStatus(self, model, item, slotID):
        super(_CompareEconomicBattleBoosterProvider, self)._fillStatus(model, item, slotID)
        model.setLockReason('compare')
        model.setIsLocked(True)


class _CompareBattleBoostersTabsController(BattleBoostersTabsController):

    def _getAllProviders(self):
        return {BattleBoosterTabs.OPT_DEVICE: _CompareOptDeviceBattleBoosterProvider,
         BattleBoosterTabs.CREW: _CompareCrewBattleBoosterProvider,
         BattleBoosterTabs.ECONOMIC: _CompareEconomicBattleBoosterProvider}


class CompareBattleBoosterSetupSubView(CompareBaseSetupSubView):

    def _createTabsController(self):
        return _CompareBattleBoostersTabsController()
