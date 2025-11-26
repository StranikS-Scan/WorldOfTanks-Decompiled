# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/tooltips/royale_lobby_builders.py
from frameworks.wulf import WindowLayer
from battle_royale.gui.Scaleform.daapi.view.lobby.tooltips import BattleProgressionTooltipData, BattleRoyaleCalendarExtendedTooltip
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader import sf_lobby
from gui.shared.tooltips import contexts
from battle_royale.gui.shared.tooltips.battle_royale_modules import BattleRoyaleModulesTooltip
from gui.shared.tooltips.builders import DataBuilder
from battle_royale.gui.Scaleform.daapi.view.lobby.tooltips.battle_royale_completed_quest_tooltip import BattleRoyaleQuestsTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_MODULES_HANGAR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleRoyaleModulesTooltip(_BattleRoyaleHangarVehInfoContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_BATTLE_PROGRESSION, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleProgressionTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_CALENDAR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleRoyaleCalendarExtendedTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_COMPLETED_QUESTS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleRoyaleQuestsTooltip(contexts.QuestsBoosterContext())))


class _BattleRoyaleHangarVehInfoContext(contexts.HangarContext):

    @sf_lobby
    def app(self):
        return None

    def getVehicle(self):
        hangarVehConfigurator = self.app.containerManager.getContainer(WindowLayer.SUB_VIEW).getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW})
        return hangarVehConfigurator.getSelectedVehicle()

    def buildItem(self, intCD, slotIdx=0, historicalBattleID=-1, vehicle=None):
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
