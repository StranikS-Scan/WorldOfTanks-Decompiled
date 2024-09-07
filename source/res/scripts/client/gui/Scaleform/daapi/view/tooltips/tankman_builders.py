# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tankman_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.crew.tooltips.advanced_tooltip_view import AdvancedTooltipView
from gui.impl.lobby.crew.tooltips.commander_bonus_additional_tooltip import CommanderBonusAdditionalTooltip
from gui.impl.lobby.crew.tooltips.commander_bonus_tooltip import CommanderBonusTooltip
from gui.impl.lobby.crew.tooltips.crew_perks_additional_tooltip import CrewPerksAdditionalTooltip, BattleRoyaleCrewPerksAdditionalTooltip
from gui.impl.lobby.crew.tooltips.crew_perks_tooltip import CrewPerksTooltip
from gui.impl.lobby.crew.tooltips.tankman_tooltip import TankmanTooltip
from gui.shared.tooltips import advanced
from gui.shared.tooltips import contexts, ToolTipBaseData
from gui.shared.tooltips import tankman
from gui.shared.tooltips.advanced import TANKMAN_MOVIES
from gui.shared.tooltips.builders import DataBuilder, AdvancedTooltipWindowBuilder
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
__all__ = ('getTooltipBuilders',)

def _advancedPerkCondition(skillName, *_):
    return skillName in advanced.SKILL_MOVIES


class BattleRoyaleTankmanTooltipBuilder(DataBuilder):
    __slots__ = ()
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, tooltipType, linkage):
        context = contexts.TankmanHangarContext()
        dataBlock = tankman.BattleRoyaleTankmanTooltipDataBlock(context)
        super(BattleRoyaleTankmanTooltipBuilder, self).__init__(tooltipType, linkage, dataBlock)

    def _buildData(self, _advanced, invID, *args, **kwargs):
        return super(BattleRoyaleTankmanTooltipBuilder, self)._buildData(_advanced, invID)


class NotRecruitedTankmanTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(NotRecruitedTankmanTooltipBuilder, self).__init__(tooltipType, linkage, tankman.NotRecruitedTooltipData(contexts.NotRecruitedTankmanContext()))

    def _buildData(self, _advanced, invID, *args, **kwargs):
        return super(NotRecruitedTankmanTooltipBuilder, self)._buildData(_advanced, invID)


class CrewPerkTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CrewPerkTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.CREW_PERK_GF)

    def getDisplayableData(self, skillName, tankmanId, skillLevel=None, isCommonExtraAvailable=False, showAdditionalInfo=True, parent=None, *args, **kwargs):
        return DecoratedTooltipWindow(CrewPerksTooltip(skillName, tankmanId, skillLevel, isCommonExtraAvailable, showAdditionalInfo), parent, False)

    def buildToolTip(self, *args, **kwargs):
        return {'type': self.getType(),
         'component': self.context.getComponent()}

    def setSupportAdvanced(self, supportAdvanced):
        pass


class CrewPerkTooltipDataAdditional(CrewPerkTooltipData):

    def getDisplayableData(self, skillName, tankmanId, skillLevel=None, isCommonExtraAvailable=False, showAdditionalInfo=True, parent=None, *args, **kwargs):
        return DecoratedTooltipWindow(CrewPerksAdditionalTooltip(skillName, tankmanId), parent, False)


class BattleRoyaleCrewPerkTooltipDataAdditional(CrewPerkTooltipData):

    def getDisplayableData(self, skillName, tankmanId, skillLevel=None, isCommonExtraAvailable=False, showAdditionalInfo=True, parent=None, *args, **kwargs):
        return DecoratedTooltipWindow(BattleRoyaleCrewPerksAdditionalTooltip(skillName, tankmanId), parent, False)


class CommanderBonusTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CommanderBonusTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.COMMANDER_BONUS)

    def getDisplayableData(self, parent=None, *args, **kwargs):
        return DecoratedTooltipWindow(CommanderBonusTooltip(), parent, useDecorator=False)


class CommanderBonusTooltipDataAdditional(CommanderBonusTooltipData):

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(CommanderBonusAdditionalTooltip(), useDecorator=False)


class TankmanTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(TankmanTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.TANKMAN)

    def getDisplayableData(self, parent=None, *args, **kwargs):
        return DecoratedTooltipWindow(TankmanTooltip(*args, **kwargs), parent, useDecorator=False)


class TankmanTooltipAdditional(ToolTipBaseData):

    def __init__(self, context):
        super(TankmanTooltipAdditional, self).__init__(context, None)
        return

    def getDisplayableData(self, parent=None, *args, **kwargs):
        item = self.context.buildItem(*args, **kwargs)
        return DecoratedTooltipWindow(AdvancedTooltipView(TANKMAN_MOVIES[item.role], item.roleUserName, backport.text(R.strings.tooltips.advanced.dyn(item.role)())), parent, useDecorator=False)


def getTooltipBuilders():
    return (NotRecruitedTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     BattleRoyaleTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.CREW_PERK_GF, None, CrewPerkTooltipData(contexts.ToolTipContext(None)), CrewPerkTooltipDataAdditional(contexts.ToolTipContext(None)), condition=_advancedPerkCondition),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_CREW_PERK_GF, None, CrewPerkTooltipData(contexts.ToolTipContext(None)), BattleRoyaleCrewPerkTooltipDataAdditional(contexts.ToolTipContext(None)), condition=_advancedPerkCondition),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.COMMANDER_BONUS, None, CommanderBonusTooltipData(contexts.ToolTipContext(None)), CommanderBonusTooltipDataAdditional(contexts.ToolTipContext(None))),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.TANKMAN, None, TankmanTooltipData(contexts.TankmanHangarContext()), TankmanTooltipAdditional(contexts.TankmanHangarContext())))
