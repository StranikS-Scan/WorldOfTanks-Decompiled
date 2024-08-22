# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tankman_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.crew.tooltips.advanced_tooltip_view import AdvancedTooltipView
from gui.impl.lobby.crew.tooltips.commander_bonus_additional_tooltip import CommanderBonusAdditionalTooltip
from gui.impl.lobby.crew.tooltips.commander_bonus_tooltip import CommanderBonusTooltip
from gui.impl.lobby.crew.tooltips.crew_perks_additional_tooltip import CrewPerksAdditionalTooltip
from gui.impl.lobby.crew.tooltips.crew_perks_tooltip import CrewPerksTooltip
from gui.impl.lobby.crew.tooltips.empty_skill_tooltip import EmptySkillTooltip
from gui.impl.lobby.crew.tooltips.skill_untrained_additional_tooltip import SkillUntrainedAdditionalTooltip
from gui.impl.lobby.crew.tooltips.skill_untrained_tooltip import SkillUntrainedTooltip
from gui.impl.lobby.crew.tooltips.skills_efficiency_tooltip import SkillsEfficiencyTooltip
from gui.impl.lobby.crew.tooltips.tankman_tooltip import TankmanTooltip
from gui.shared.tooltips import advanced
from gui.shared.tooltips import contexts, ToolTipBaseData
from gui.shared.tooltips import tankman
from gui.shared.tooltips.advanced import TANKMAN_MOVIES
from gui.shared.tooltips.builders import DataBuilder, AdvancedTooltipWindowBuilder, TooltipWindowBuilder
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
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


class SpecialTankmanTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(SpecialTankmanTooltipBuilder, self).__init__(tooltipType, linkage, tankman.SpecialTankmanTooltipData(contexts.HangarContext()))


class CrewPerkTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CrewPerkTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.CREW_PERK_GF)

    def getDisplayableData(self, skillName, tankmanId, skillLevel=None, showAdditionalInfo=True, skillCustomisation=None, isBonus=None, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        return DecoratedTooltipWindow(CrewPerksTooltip(skillName, tankmanId, skillLevel, showAdditionalInfo, skillCustomisation=skillCustomisation, isBonus=isBonus), parent, False)

    def buildToolTip(self, *args, **kwargs):
        return {'type': self.getType(),
         'component': self.context.getComponent()}

    def setSupportAdvanced(self, supportAdvanced):
        pass


class CrewPerkTooltipDataAdditional(CrewPerkTooltipData):

    def getDisplayableData(self, skillName, tankmanId, skillLevel=None, isCommonExtraAvailable=False, showAdditionalInfo=True, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        return DecoratedTooltipWindow(CrewPerksAdditionalTooltip(skillName, tankmanId), parent, False)


class SkillUntrainedTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SkillUntrainedTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED)

    def getDisplayableData(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        return DecoratedTooltipWindow(SkillUntrainedTooltip(), parent, useDecorator=False)


class SkillUntrainedTooltipDataAdditional(SkillUntrainedTooltipData):

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(SkillUntrainedAdditionalTooltip(), useDecorator=False)


class CommanderBonusTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CommanderBonusTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.COMMANDER_BONUS)

    def getDisplayableData(self, tankmanId=None, *args, **kwargs):
        parent = kwargs.get('parent', None)
        return DecoratedTooltipWindow(CommanderBonusTooltip(tankmanId), parent, useDecorator=False)


class CommanderBonusTooltipDataAdditional(CommanderBonusTooltipData):

    def getDisplayableData(self, tankmanId=None, *args, **kwargs):
        return DecoratedTooltipWindow(CommanderBonusAdditionalTooltip(tankmanId), useDecorator=False)


class TankmanTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(TankmanTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.TANKMAN)

    def getDisplayableData(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        kwargs['layoutID'] = parent.content.layoutID if parent else None
        return DecoratedTooltipWindow(TankmanTooltip(*args, **kwargs), parent, useDecorator=False)


class TankmanTooltipAdditional(ToolTipBaseData):

    def __init__(self, context):
        super(TankmanTooltipAdditional, self).__init__(context, None)
        return

    def getDisplayableData(self, tankmanID=None, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        item = self.context.buildItem(tankmanID, **kwargs)
        return DecoratedTooltipWindow(AdvancedTooltipView(TANKMAN_MOVIES[item.role], item.roleUserName, backport.text(R.strings.tooltips.advanced.dyn(item.role)())), parent, useDecorator=False)


class SkillsEfficiencyTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SkillsEfficiencyTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.SKILLS_EFFICIENCY)

    def getDisplayableData(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        return DecoratedTooltipWindow(SkillsEfficiencyTooltip(*args, **kwargs), parent, useDecorator=False)


class SkillsEfficiencyTooltipAdditional(ToolTipBaseData):

    def __init__(self, context):
        super(SkillsEfficiencyTooltipAdditional, self).__init__(context, None)
        return

    def getDisplayableData(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        return DecoratedTooltipWindow(AdvancedTooltipView('skillEfficiency', backport.text(R.strings.tooltips.skillsEfficiency.header()), backport.text(R.strings.tooltips.skillsEfficiency.altDescription())), parent, useDecorator=False)


class EmptySkillTooltipData(ToolTipBaseData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(EmptySkillTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.EMPTY_SKILL_GF)

    def getDisplayableData(self, tankmanId, *args, **kwargs):
        tman = self.itemsCache.items.getTankman(tankmanId)
        allSkillCount, _ = tman.descriptor.getTotalSkillsProgress(withFree=True)
        lasSkillIdx = max(allSkillCount - 1, 0)
        parent = kwargs.pop('parent', None)
        return DecoratedTooltipWindow(EmptySkillTooltip(tman, lasSkillIdx), parent, useDecorator=False)


def getTooltipBuilders():
    return (NotRecruitedTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     BattleRoyaleTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     SpecialTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.SPECIAL_TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.CREW_PERK_GF, None, CrewPerkTooltipData(contexts.ToolTipContext(None)), CrewPerkTooltipDataAdditional(contexts.ToolTipContext(None)), condition=_advancedPerkCondition),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.CREW_PERK_ALT_GF, None, CrewPerkTooltipDataAdditional(contexts.ToolTipContext(None))),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.CREW_SKILL_UNTRAINED, None, SkillUntrainedTooltipData(contexts.ToolTipContext(None)), SkillUntrainedTooltipDataAdditional(contexts.ToolTipContext(None))),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.COMMANDER_BONUS, None, CommanderBonusTooltipData(contexts.ToolTipContext(None)), CommanderBonusTooltipDataAdditional(contexts.ToolTipContext(None))),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.TANKMAN, None, TankmanTooltipData(contexts.TankmanHangarContext()), TankmanTooltipAdditional(contexts.TankmanHangarContext())),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.SKILLS_EFFICIENCY, None, SkillsEfficiencyTooltipData(contexts.ToolTipContext(None)), SkillsEfficiencyTooltipAdditional(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EMPTY_SKILL_GF, None, EmptySkillTooltipData(contexts.ToolTipContext(None))))
