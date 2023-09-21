# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/tooltips/frontline_battle_builders.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from frontline.gui.shared.tooltips.FLRandomReserve import FLRandomReserve
from gui.app_loader import sf_battle
from gui.shared.tooltips.builders import DataBuilder
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_RANDOM_RESERVE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FLRandomReserve(_FLRandomReserveContext())),)


class _FLRandomReserveContext(ConsumablesPanel):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _EQUIPMENT_ARG = 0

    @sf_battle
    def app(self):
        return None

    def buildItem(self, *args, **kwargs):
        equipment = self.__sessionProvider.shared.equipments.getEquipmentByIDx(args[self._EQUIPMENT_ARG] - self._ORDERS_START_IDX)
        return equipment

    def getComponent(self):
        return None
