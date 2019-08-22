# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/royale_battle_builders.py
from gui.Scaleform.daapi.view.battle.battle_royale.tooltips import WeakZonesTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader import sf_battle
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips.battle_royale_modules import BattleRoyaleModulesTooltip
from gui.shared.tooltips.builders import DataBuilder
from helpers import dependency
from items import parseIntCompactDescr
from skeletons.gui.battle_session import IBattleSessionProvider
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_MODULES, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleRoyaleModulesTooltip(_BattleRoyaleBattleVehInfoContext())), DataBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_WEAK_ZONES, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, WeakZonesTooltip(_BattleRoyaleBattleVehInfoContext())))


class _BattleRoyaleBattleVehInfoContext(object):

    @sf_battle
    def app(self):
        return None

    def buildItem(self, *args, **kwargs):
        intCD = args[0]
        itemTypeID, _, _ = parseIntCompactDescr(intCD)
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            vehicle = self.getVehicle()
            return (vehicle, vehicle)
        module = self.__getProgressionCtrl().getModule(intCD)
        currentModule = self.__getProgressionCtrl().getInstalledAnalog(intCD)
        return (module, currentModule)

    def getVehicle(self):
        return self.__getProgressionCtrl().getCurrentVehicle()

    @dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
    def __getProgressionCtrl(self, sessionProvider=None):
        return sessionProvider.dynamic.progression

    def getComponent(self):
        return None
