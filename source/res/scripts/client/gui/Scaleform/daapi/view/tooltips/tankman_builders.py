# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/tankman_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import skill
from gui.shared.tooltips import tankman
from gui.shared.tooltips.builders import DataBuilder, ConditionBuilder
__all__ = ('getTooltipBuilders',)

class TankmanTooltipBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TankmanTooltipBuilder, self).__init__(tooltipType, linkage, tankman.TankmanTooltipData(contexts.TankmanHangarContext()))

    def _buildData(self, invID, *args):
        return super(TankmanTooltipBuilder, self)._buildData(invID)


class TankmanNewSkillTooltipBuilder(ConditionBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TankmanNewSkillTooltipBuilder, self).__init__(tooltipType, linkage, TOOLTIPS_CONSTANTS.COMPLEX_UI, skill.BuySkillTooltipData(contexts.NewSkillContext()))

    def _check(self, data):
        content = data['data']
        return content['count'] > 1 or content['level'] > 0


def getTooltipBuilders():
    return (TankmanTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN, TOOLTIPS_CONSTANTS.TANKMEN_UI),
     DataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_SKILL, TOOLTIPS_CONSTANTS.TANKMEN_SKILL_UI, skill.SkillTooltipData(contexts.PersonalCaseContext(fieldsToExclude=('count',)))),
     TankmanNewSkillTooltipBuilder(TOOLTIPS_CONSTANTS.TANKMAN_NEW_SKILL, TOOLTIPS_CONSTANTS.TANKMEN_BUY_SKILL_UI),
     DataBuilder(TOOLTIPS_CONSTANTS.TANKMAN_SKILL_EXTENDED, TOOLTIPS_CONSTANTS.TANKMAN_SKILL_EXTENDED_UI, skill.TankmanSkillTooltipData(contexts.HangarParamContext())))
