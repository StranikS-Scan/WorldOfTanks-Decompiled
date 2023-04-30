# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tankman_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.lobby.crew.tooltips.crew_perks_additional_tooltip import CrewPerksAdditionalTooltip
from gui.impl.lobby.crew.tooltips.crew_perks_tooltip import CrewPerksTooltip
from gui.shared.tooltips import advanced
from gui.shared.tooltips import contexts, ToolTipBaseData
from gui.shared.tooltips import skill
from gui.shared.tooltips import tankman
from gui.shared.tooltips.builders import AdvancedDataBuilder, ConditionBuilder, DataBuilder, AdvancedTooltipWindowBuilder
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
__all__ = ('getTooltipBuilders',)

def _advancedPerkCondition(skillName, *_):
    return skillName in advanced.SKILL_MOVIES


class TankmanTooltipBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TankmanTooltipBuilder, self).__init__(tooltipType, linkage, tankman.TankmanTooltipDataBlock(contexts.TankmanHangarContext()), advanced.TankmanTooltipAdvanced(contexts.TankmanHangarContext()))

    def _buildData(self, _advanced, invID, *args, **kwargs):
        return super(TankmanTooltipBuilder, self)._buildData(_advanced, invID)


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


class TankmanNewSkillTooltipBuilder(ConditionBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TankmanNewSkillTooltipBuilder, self).__init__(tooltipType, linkage, TOOLTIPS_CONSTANTS.COMPLEX_UI, skill.BuySkillTooltipData(contexts.NewSkillContext()))

    def _check(self, data):
        content = data['data']
        return content['count'] > 1 or content['level'] > 0


class CrewPerkTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CrewPerkTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.CREW_PERK_GF)

    def getDisplayableData(self, skillName, tankmanId, skillLevel=None, isCommonExtraAvailable=False, *args, **kwargs):
        return DecoratedTooltipWindow(CrewPerksTooltip(skillName, tankmanId, skillLevel, isCommonExtraAvailable), useDecorator=False)

    def buildToolTip(self, *args, **kwargs):
        return {'type': self.getType(),
         'component': self.context.getComponent()}

    def setSupportAdvanced(self, supportAdvanced):
        pass


class CrewPerkTooltipDataAdditional(CrewPerkTooltipData):

    def getDisplayableData(self, skillName, tankmanId, *args, **kwargs):
        return DecoratedTooltipWindow(CrewPerksAdditionalTooltip(skillName, tankmanId), useDecorator=False)


def getTooltipBuilders():
    return (TankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     NotRecruitedTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     BattleRoyaleTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     TankmanNewSkillTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NEW_SKILL, TOOLTIPS_CONSTANTS.TANKMEN_BUY_SKILL_UI),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.CREW_PERK_GF, None, CrewPerkTooltipData(contexts.ToolTipContext(None)), CrewPerkTooltipDataAdditional(contexts.ToolTipContext(None)), condition=_advancedPerkCondition))
