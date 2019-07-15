# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/epic_skills.py
from math_utils import clamp
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.COMMON import COMMON
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.battle_ability_tooltip_params import g_battleAbilityTooltipMgr
from helpers import dependency, i18n, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
_TOOLTIP_MIN_WIDTH = 400

class EpicSkillBaseTooltipData(BlocksTooltipData):
    _epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx):
        super(EpicSkillBaseTooltipData, self).__init__(ctx, TOOLTIP_TYPE.EPIC_SKILL_INFO)
        self._setMargins(afterBlock=15, afterSeparator=15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, skillID, level=None):
        items = super(EpicSkillBaseTooltipData, self)._packBlocks()
        self._constructHeader(items, skillID, int(level) if level else self._epicMetaGameCtrl.getSkillLevels().get(skillID, None))
        return items

    def _constructHeader(self, block, skillID, level):
        if level:
            romanLvl = int2roman(level)
            desc = i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_LEVEL, lvl=romanLvl)
        else:
            level = 1
            desc = EPIC_BATTLE.METAABILITYSCREEN_ABILITY_NOT_UNLOCKED
        skillLevel = self._epicMetaGameCtrl.getAllSkillsInformation()[skillID].levels[level]
        title = skillLevel.name
        icon = skillLevel.icon
        imgPaddingLeft = 20
        imgPaddingTop = 0
        txtOffset = 85
        highlightPath = None
        overlayPath = None
        overlayPadding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_OVERLAY_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_OVERLAY_PADDING_LEFT)
        highlightPadding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.TOOLTIP_HIGHLIGHT_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.TOOLTIP_HIGHLIGHT_PADDING_LEFT)
        block.append(formatters.packItemTitleDescBlockData(title=text_styles.highTitle(title), desc=text_styles.standard(desc), img=RES_ICONS.getEpicBattlesSkillIcon('43x43', icon), imgPadding=formatters.packPadding(left=imgPaddingLeft, top=imgPaddingTop), txtGap=-3, txtOffset=txtOffset, padding=formatters.packPadding(top=0, bottom=0), overlayPath=overlayPath, overlayPadding=overlayPadding, highlightPath=highlightPath, highlightPadding=highlightPadding))
        if skillLevel.longFilterAlert:
            blocks = [formatters.packTextBlockData(text_styles.standard(skillLevel.shortDescr)), formatters.packTextBlockData(text_styles.alert(skillLevel.longFilterAlert))]
            block.append(formatters.packBuildUpBlockData(blocks=blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL, padding=formatters.packPadding(left=txtOffset, top=0)))
        else:
            block.append(formatters.packTextBlockData(text_styles.standard(skillLevel.shortDescr), padding=formatters.packPadding(left=txtOffset, top=0)))
        return


class EpicSkillExtendedTooltip(EpicSkillBaseTooltipData):

    def _packBlocks(self, skillID, specLevel=None):
        headerblocks = super(EpicSkillExtendedTooltip, self)._packBlocks(skillID, specLevel)
        skillInfo = self._epicMetaGameCtrl.getAllSkillsInformation()[skillID]
        currentLvl = self._epicMetaGameCtrl.getSkillLevels().get(skillID, 1)
        specLevel = clamp(1, skillInfo.maxLvl, int(specLevel) if specLevel else currentLvl)
        bodyBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle('{}{}'.format(i18n.makeString(EPIC_BATTLE.ABILITYINFO_PROPERTIES), i18n.makeString(COMMON.COMMON_COLON))))]
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
        return [formatters.packTitleDescBlock(EPIC_BATTLE.ABILITYINFO_MANAGE_ABILITIES, EPIC_BATTLE.ABILITYINFO_MANAGE_ABILITIES_DESC)] if eqCompDescr == -1 else super(EpicSkillSlotTooltip, self)._packBlocks(_equipmentToEpicSkillConverter(self._epicMetaGameCtrl, eqCompDescr), None)
