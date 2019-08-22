# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/royale_lobby_builders.py
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips import VehicleTooltipData, BattleProgressionTooltipData, EquipmentsTooltipData
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.perf_attention_tooltip import PerfAttentionSimpleTooltip, PerfAttentionAdvancedTooltip
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.royale_prime_calendar import RoyalePrimeTimeCalendarTooltip
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.royale_selector_items import BattleRoyaleSelectorTooltip
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.royale_server_prime_time import RoyaleServerPrimeTime
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.title_step_tooltip import TitleStepTooltip
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.title_tooltip import TitleTooltip
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader import sf_lobby
from gui.shared.tooltips import contexts
from gui.shared.tooltips.battle_royale_modules import BattleRoyaleModulesTooltip
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_MODULES_HANGAR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleRoyaleModulesTooltip(_BattleRoyaleHangarVehInfoContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_VEHICLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, VehicleTooltipData(contexts.InventoryContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_BATTLE_PROGRESSION, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleProgressionTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_EQUIPMENT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EquipmentsTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TITLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, TitleTooltip(contexts.BattleRoyaleContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_STEP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, TitleStepTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PRIME_TIMES, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RoyalePrimeTimeCalendarTooltip(contexts.ToolTipContext(None))),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SERVER_PRIME_TIME, TOOLTIPS_CONSTANTS.COMPLEX_UI, RoyaleServerPrimeTime(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PERF_SIMPLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, PerfAttentionSimpleTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PERF_ADVANCED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, PerfAttentionAdvancedTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleRoyaleSelectorTooltip(contexts.ToolTipContext(None))))


class _BattleRoyaleHangarVehInfoContext(contexts.HangarContext):

    @sf_lobby
    def app(self):
        return None

    def getVehicle(self):
        hangarVehConfigurator = self.app.containerManager.getContainer(ViewTypes.LOBBY_SUB).getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW})
        return hangarVehConfigurator.getSelectedVehicle()

    def buildItem(self, intCD, slotIdx=0, historicalBattleID=-1):
        self._vehicle = self.getVehicle()
        vDescr = self._vehicle.descriptor
        module = self.itemsCache.items.getItemByCD(intCD)
        if module is None:
            return (None, None)
        elif module == self._vehicle:
            return (module, module)
        else:
            currModuleDescr, _ = vDescr.getComponentsByType(module.itemTypeName)
            currentModule = self.itemsCache.items.getItemByCD(currModuleDescr.compactDescr)
            return (module, currentModule)
