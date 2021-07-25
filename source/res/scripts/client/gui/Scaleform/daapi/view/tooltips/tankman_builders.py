# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tankman_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import skill
from gui.shared.tooltips import tankman
from gui.shared.tooltips import advanced
from gui.shared.tooltips.builders import AdvancedDataBuilder, ConditionBuilder, DataBuilder
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
__all__ = ('getTooltipBuilders',)

def _advancedBlockCondition(context):

    def advancedTooltipExist(*args):
        item = context.buildItem(*args)
        return item.name in advanced.SKILL_MOVIES

    return advancedTooltipExist


class TankmanTooltipBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TankmanTooltipBuilder, self).__init__(tooltipType, linkage, tankman.TankmanTooltipDataBlock(contexts.ToolTipContext(None)), advanced.TankmanTooltipAdvanced(contexts.TankmanHangarContext()))
        return


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


def getTooltipBuilders():
    return (TankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     NotRecruitedTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     BattleRoyaleTankmanTooltipBuilder(TOOLTIPS_CONSTANTS.BATTLE_ROYALE_TANKMAN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_SKILL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, skill.SkillTooltipDataBlock(contexts.PersonalCaseContext(fieldsToExclude=('count',))), advanced.SkillTooltipAdvanced(contexts.PersonalCaseContext(fieldsToExclude=('count',))), condition=_advancedBlockCondition(contexts.PersonalCaseContext(fieldsToExclude=('count',)))),
     TankmanNewSkillTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NEW_SKILL, TOOLTIPS_CONSTANTS.TANKMEN_BUY_SKILL_UI),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.PREVIEW_CREW_SKILL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, skill.SkillTooltipDataBlock(contexts.PreviewCaseContext()), advanced.SkillTooltipAdvanced(contexts.PreviewCaseContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_SKILL_EXTENDED, TOOLTIPS_CONSTANTS.TANKMAN_SKILL_EXTENDED_UI, skill.TankmanSkillTooltipData(contexts.HangarParamContext()), advanced.SkillExtendedTooltipAdvanced(contexts.HangarParamContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_DEMOBILIZED_STATE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, tankman.TankmanDemobilizedStateTooltipData(contexts.TankmanHangarContext())))
