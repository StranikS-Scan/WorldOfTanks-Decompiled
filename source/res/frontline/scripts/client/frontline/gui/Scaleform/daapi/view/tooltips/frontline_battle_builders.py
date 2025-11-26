# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/tooltips/frontline_battle_builders.py
from frontline.gui.impl.lobby.tooltips.battle_ability_alt_tooltip import BattleAbilityAltTooltipView
from frontline.gui.impl.lobby.tooltips.battle_ability_tooltip import BattleAbilityTooltipView
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader import sf_battle
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.shared.tooltips import ToolTipBaseData
from gui.shared.tooltips.builders import AdvancedTooltipWindowBuilder, DataBuilder
from helpers import dependency
from frontline.gui.shared.tooltips.FLRandomReserve import FLRandomReserve
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.tooltips import contexts
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_RANDOM_RESERVE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FLRandomReserve(_FLRandomReserveContext())), AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_BATTLE_ABILITY, None, BattleAbilityTooltipData(contexts.ToolTipContext(None)), BattleAbilityAltTooltipData(contexts.ToolTipContext(None))))


class BattleAbilityTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(BattleAbilityTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.FRONTLINE_BATTLE_ABILITY)

    @staticmethod
    def getDisplayableData(intCD, *args, **kwargs):
        parent = kwargs.get('parent', None)
        return DecoratedTooltipWindow(BattleAbilityTooltipView(intCD, *args, **kwargs), parent, useDecorator=False)


class BattleAbilityAltTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(BattleAbilityAltTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.FRONTLINE_BATTLE_ABILITY)

    @staticmethod
    def getDisplayableData(intCD, *args, **kwargs):
        parent = kwargs.get('parent', None)
        return DecoratedTooltipWindow(BattleAbilityAltTooltipView(intCD, *args, **kwargs), parent, useDecorator=False)


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
