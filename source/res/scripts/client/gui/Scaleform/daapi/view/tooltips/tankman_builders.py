# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tankman_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import skill
from gui.shared.tooltips import tankman
from gui.shared.tooltips import advanced
from gui.shared.tooltips.builders import AdvancedDataBuilder, ConditionBuilder, DataBuilder
__all__ = ('getTooltipBuilders',)

class TankmanTooltipBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TankmanTooltipBuilder, self).__init__(tooltipType, linkage, tankman.TankmanTooltipDataBlock(contexts.TankmanHangarContext()), advanced.TankmanTooltipAdvanced(contexts.TankmanHangarContext()))

    def _buildData(self, _advanced, invID, *args, **kwargs):
        return super(TankmanTooltipBuilder, self)._buildData(_advanced, invID)


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
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_SKILL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, skill.SkillTooltipDataBlock(contexts.PersonalCaseContext(fieldsToExclude=('count',))), advanced.SkillTooltipAdvanced(contexts.PersonalCaseContext(fieldsToExclude=('count',)))),
     TankmanNewSkillTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NEW_SKILL, TOOLTIPS_CONSTANTS.TANKMEN_BUY_SKILL_UI),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_SKILL_EXTENDED, TOOLTIPS_CONSTANTS.TANKMAN_SKILL_EXTENDED_UI, skill.TankmanSkillTooltipData(contexts.HangarParamContext()), advanced.SkillExtendedTooltipAdvanced(contexts.HangarParamContext())))
