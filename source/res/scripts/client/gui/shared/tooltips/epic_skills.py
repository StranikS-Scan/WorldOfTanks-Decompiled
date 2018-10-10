# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/epic_skills.py
from AvatarInputHandler.mathUtils import clamp
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.locale.COMMON import COMMON
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.daapi.view.lobby.epicBattle.battle_ability_tooltip_params import g_battleAbilityParamsRenderers
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from items import vehicles
_TOOLTIP_MIN_WIDTH = 400

class EpicSkillBaseTooltipData(BlocksTooltipData):
    _epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, ctx):
        super(EpicSkillBaseTooltipData, self).__init__(ctx, TOOLTIP_TYPE.EPIC_SKILL_INFO)
        self._setMargins(afterBlock=15, afterSeparator=15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, skillID, level=None):
        items = super(EpicSkillBaseTooltipData, self)._packBlocks()
        self._constructHeader(items, skillID, int(level) if level else self._epicMetaGameCtrl.getSkillLevels().get(skillID, 1))
        return items

    def _constructHeader(self, block, skillID, level):
        skillLevel = self._epicMetaGameCtrl.getSkillInformation()[skillID].levels[level]
        title = skillLevel.name
        icon = skillLevel.icon
        romanLvl = int2roman(level)
        desc = i18n.makeString(EPIC_BATTLE.METAABILITYSCREEN_ABILITY_LEVEL, lvl=romanLvl)
        imgPaddingLeft = 20
        imgPaddingTop = 0
        txtOffset = 85
        highlightPath = None
        overlayPath = None
        padding = formatters.packPadding(top=SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_PADDING_TOP, left=SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_PADDING_LEFT)
        block.append(formatters.packItemTitleDescBlockData(title=text_styles.highTitle(title), desc=text_styles.standard(desc), img=RES_ICONS.getEpicBattlesSkillIcon('43x43', icon), imgPadding=formatters.packPadding(left=imgPaddingLeft, top=imgPaddingTop), txtGap=-3, txtOffset=txtOffset, padding=formatters.packPadding(top=0, bottom=0), overlayPath=overlayPath, overlayPadding=padding, highlightPath=highlightPath, highlightPadding=padding))
        block.append(formatters.packTextBlockData(text_styles.standard(skillLevel.shortDescr), padding=formatters.packPadding(left=txtOffset, top=0)))
        return


class EpicSkillExtendedTooltip(EpicSkillBaseTooltipData):

    def _packBlocks(self, skillID, specLevel=None):
        headerblocks = super(EpicSkillExtendedTooltip, self)._packBlocks(skillID, specLevel)
        skillInfo = self._epicMetaGameCtrl.getSkillInformation()[skillID]
        currentLvl = self._epicMetaGameCtrl.getSkillLevels().get(skillID, 1)
        specLevel = clamp(1, skillInfo.maxLvl, int(specLevel) if specLevel else currentLvl)
        eqs = vehicles.g_cache.equipments()
        levels = skillInfo.levels
        curLvlEq = eqs[levels[currentLvl].eqID]
        specLvlEq = eqs[levels[specLevel].eqID]
        bodyBlocks = [formatters.packTextBlockData(text=text_styles.middleTitle('{}{}'.format(i18n.makeString(EPIC_BATTLE.ABILITYINFO_PROPERTIES), i18n.makeString(COMMON.COMMON_COLON))))]
        for tooltipInfo in eqs[skillInfo.levels[currentLvl].eqID].tooltipInformation:
            renderer = g_battleAbilityParamsRenderers.get(tooltipInfo.renderer, None)
            if renderer:
                renderer(bodyBlocks, curLvlEq, specLvlEq, (eqs[lvl.eqID] for lvl in levels.itervalues()), tooltipInfo.identifier, tooltipInfo.name)

        bodyBlock = formatters.packBuildUpBlockData(bodyBlocks, gap=15)
        headerblocks.append(bodyBlock)
        return headerblocks


def _equipmentToEpicSkillConverter(epicMetaGameCtrl, eqCompDescr):
    convertedEqCompDescr = int(eqCompDescr) >> 8 & 65535
    skillID = next((abilityID for abilityID, skillInfo in epicMetaGameCtrl.getSkillInformation().iteritems() if convertedEqCompDescr in (lvl.eqID for lvl in skillInfo.levels.itervalues())), 0)
    if skillID == 0:
        LOG_ERROR('Could not find the epic skill corresponding to the given eqCompDescr: ' + str(eqCompDescr))
    return skillID


class EpicSkillSlotTooltip(EpicSkillBaseTooltipData):

    def _packBlocks(self, eqCompDescr, _=None):
        return [formatters.packTitleDescBlock(EPIC_BATTLE.ABILITYINFO_MANAGE_ABILITIES, EPIC_BATTLE.ABILITYINFO_MANAGE_ABILITIES_DESC)] if eqCompDescr == -1 else super(EpicSkillSlotTooltip, self)._packBlocks(_equipmentToEpicSkillConverter(self._epicMetaGameCtrl, eqCompDescr), None)
