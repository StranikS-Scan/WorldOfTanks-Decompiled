# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/epic_skills.py
from math_utils import clamp
from debug_utils import LOG_ERROR
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.battle_ability_tooltip_params import g_battleAbilityTooltipMgr
from helpers import dependency, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
_TOOLTIP_MIN_WIDTH = 460

class EpicSkillBaseTooltipData(BlocksTooltipData):
    _epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx):
        super(EpicSkillBaseTooltipData, self).__init__(ctx, TOOLTIP_TYPE.EPIC_SKILL_INFO)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, skillID, level=None):
        items = super(EpicSkillBaseTooltipData, self)._packBlocks()
        realLevel = int(level) if level else self._epicMetaGameCtrl.getSkillLevels().get(skillID, None)
        skillLevel = self._epicMetaGameCtrl.getAllSkillsInformation()[skillID].levels[realLevel if realLevel else 1]
        items.append(formatters.packBuildUpBlockData(self._constructHeader(skillLevel, realLevel), padding=formatters.packPadding(top=4, bottom=-1)))
        items.append(formatters.packBuildUpBlockData(self.__constructDescr(skillLevel), padding=formatters.packPadding(top=-5, bottom=-8), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        if not realLevel:
            items.append(formatters.packBuildUpBlockData(self.__constructInactiveStateBlock(), padding=formatters.packPadding(top=-6, bottom=-21)))
        return items

    def _constructHeader(self, skillLevel, level):
        block = []
        if level:
            romanLvl = int2roman(level)
            desc = backport.text(R.strings.epic_battle.metaAbilityScreen.Ability_level(), lvl=text_styles.expText(romanLvl))
            descFormatter = text_styles.main
        else:
            desc = backport.text(R.strings.epic_battle.metaAbilityScreen.Ability_not_unlocked())
            descFormatter = text_styles.standard
        block.append(formatters.packTitleDescBlock(title=text_styles.highTitle(skillLevel.name), desc=descFormatter(desc), gap=-5))
        block.append(formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.epicBattles.skills.c_176x176.dyn(skillLevel.icon)()), padding=formatters.packPadding(left=123, top=10)))
        return block

    def __constructDescr(self, skillLevel):
        block = []
        if skillLevel.longFilterAlert:
            blocks = [formatters.packTextBlockData(text_styles.standard(skillLevel.longDescr)), formatters.packTextBlockData(text_styles.alert(skillLevel.longFilterAlert))]
            block.append(formatters.packBuildUpBlockData(blocks=blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL))
        else:
            block.append(formatters.packTextBlockData(text_styles.main(skillLevel.longDescr)))
        return block

    def __constructInactiveStateBlock(self):
        return [formatters.packTitleDescBlock(title=text_styles.critical(backport.text(R.strings.epic_battle.metaAbilityScreen.Ability_not_unlocked())), desc=text_styles.standard(backport.text(R.strings.epic_battle.metaAbilityScreen.how_to_activate())), gap=2)]


class EpicSkillExtendedTooltip(EpicSkillBaseTooltipData):

    def _packBlocks(self, skillID, specLevel=None):
        headerblocks = super(EpicSkillExtendedTooltip, self)._packBlocks(skillID, specLevel)
        skillInfo = self._epicMetaGameCtrl.getAllSkillsInformation()[skillID]
        currentLvl = self._epicMetaGameCtrl.getSkillLevels().get(skillID, 1)
        specLevel = clamp(1, skillInfo.maxLvl, int(specLevel) if specLevel else currentLvl)
        bodyBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle('{}{}'.format(backport.text(R.strings.epic_battle.abilityInfo.properties()), backport.text(R.strings.common.common.colon()))))]
        g_battleAbilityTooltipMgr.createBattleAbilityTooltipRenderers(skillInfo, currentLvl, specLevel, bodyBlocks)
        bodyBlock = formatters.packBuildUpBlockData(bodyBlocks, gap=15)
        headerblocks.append(bodyBlock)
        return headerblocks


def _equipmentToEpicSkillConverter(epicMetaGameCtrl, eqCompDescr):
    convertedEqCompDescr = int(eqCompDescr) >> 8 & 65535
    skillID = next((abilityID for abilityID, skillInfo in epicMetaGameCtrl.getAllSkillsInformation().iteritems() if convertedEqCompDescr in (lvl.eqID for lvl in skillInfo.levels.itervalues())), 0)
    if skillID == 0:
        LOG_ERROR('Could not find the epic skill corresponding to the given eqCompDescr: ' + str(eqCompDescr))
    return skillID


class EpicSkillSlotTooltip(EpicSkillBaseTooltipData):

    def _packBlocks(self, eqCompDescr, _=None):
        return [formatters.packTitleDescBlock(backport.text(R.strings.epic_battle.abilityInfo.manage_abilities()), backport.text(R.strings.epic_battle.abilityInfo.manage_abilities_desc()))] if eqCompDescr == -1 else super(EpicSkillSlotTooltip, self)._packBlocks(_equipmentToEpicSkillConverter(self._epicMetaGameCtrl, eqCompDescr), None)
