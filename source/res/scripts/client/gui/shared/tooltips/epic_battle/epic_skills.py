# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/epic_battle/epic_skills.py
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, Vehicle
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.battle_ability_tooltip_params import g_battleAbilityTooltipMgr
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
_TOOLTIP_MIN_WIDTH = 460
_SETUP_INFO_TOOLTIP_MIN_WIDTH = 440

class EpicSkillBaseTooltipData(BlocksTooltipData):
    _epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(EpicSkillBaseTooltipData, self).__init__(ctx, TOOLTIP_TYPE.EPIC_SKILL_INFO)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, skillID, level=None):
        items = super(EpicSkillBaseTooltipData, self)._packBlocks()
        skillInfo = self._epicMetaGameCtrl.getAllSkillsInformation().get(skillID)
        skillLevel = skillInfo.levels.get(1) if skillInfo else None
        if skillInfo is None or skillLevel is None:
            return items
        else:
            items.append(formatters.packBuildUpBlockData(self._constructHeader(skillLevel), padding=formatters.packPadding(top=4, bottom=-1)))
            items.append(formatters.packBuildUpBlockData(self.__constructDescr(skillLevel), padding=formatters.packPadding(top=-5, bottom=-8), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
            statBlocks = self.__constructStatsBlock(skillInfo)
            for i, _ in enumerate(statBlocks):
                linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE if i == 1 else BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE
                items.append(formatters.packBuildUpBlockData(statBlocks[i], linkage=linkage))

            realLevel = self._epicMetaGameCtrl.getSkillLevels().get(skillID)
            if not realLevel:
                items.append(formatters.packBuildUpBlockData(self.__constructInactiveStateBlock(skillInfo), padding=formatters.packPadding(top=-6, bottom=-21)))
            return items

    def _constructHeader(self, skillLevel):
        block = [formatters.packTitleDescBlock(title=text_styles.highTitle(skillLevel.name), gap=-5), formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.epicBattles.skills.c_176x176.dyn(skillLevel.icon)()), width=128, height=128, padding=formatters.packPadding(left=123, top=-10))]
        return block

    def __constructDescr(self, skillLevel):
        block = []
        if skillLevel.longFilterAlert:
            blocks = [formatters.packTextBlockData(text_styles.standard(skillLevel.longDescr)), formatters.packTextBlockData(text_styles.alert(skillLevel.longFilterAlert))]
            block.append(formatters.packBuildUpBlockData(blocks=blocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL))
        else:
            block.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.onUse())), desc=text_styles.main(skillLevel.longDescr)))
        return block

    def __constructStatsBlock(self, skillInfo):
        blocks = []
        staticBlocks = []
        dynamicBlocks = []
        staticBlock = []
        dynamicBlock = []
        g_battleAbilityTooltipMgr.createBattleAbilityTooltipRenderers(skillInfo, staticBlock, dynamicBlock)
        if staticBlock:
            staticBlocks.append(formatters.packTextBlockData(text=text_styles.middleTitle('{}{}'.format(backport.text(R.strings.epic_battle.abilityInfo.properties.static()), backport.text(R.strings.common.common.colon()))), padding=formatters.packPadding(bottom=5)))
            staticBlocks.extend(staticBlock)
            blocks.append(staticBlocks)
        if dynamicBlock:
            dynamicBlocks.append(formatters.packTextBlockData(text=text_styles.middleTitle('{}{}'.format(backport.text(R.strings.epic_battle.abilityInfo.properties.dynamic()), backport.text(R.strings.common.common.colon()))), padding=formatters.packPadding(bottom=10)))
            dynamicBlocks.append(formatters.packAbilityBattleRanksBlockData())
            dynamicBlocks.extend(dynamicBlock)
            dynamicBlocks.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.epic_battle.metaAbilityScreen.activation_depends())), padding=formatters.packPadding(top=12)))
            blocks.append(dynamicBlocks)
        return blocks

    @staticmethod
    def __constructInactiveStateBlock(skillInfo):
        return [formatters.packTitleDescBlock(title=text_styles.critical(backport.text(R.strings.epic_battle.metaAbilityScreen.Ability_not_unlocked())), desc=text_styles.standard(backport.text(R.strings.epic_battle.metaAbilityScreen.how_to_activate(), price=text_styles.stats(skillInfo.price), img=icons.makeImageTag(backport.image(R.images.gui.maps.icons.epicBattles.awards.c_16x16.abilityToken()), vSpace=-3))), gap=2)]


def _equipmentToEpicSkillConverter(epicMetaGameCtrl, eqCompDescr):
    convertedEqCompDescr = int(eqCompDescr) >> 8 & 65535
    skillID = next((abilityID for abilityID, skillInfo in epicMetaGameCtrl.getAllSkillsInformation().iteritems() if convertedEqCompDescr in (lvl.eqID for lvl in skillInfo.levels.itervalues())), 0)
    if skillID == 0:
        LOG_ERROR('Could not find the epic skill corresponding to the given eqCompDescr: ' + str(eqCompDescr))
    return skillID


class EpicSkillSlotTooltip(EpicSkillBaseTooltipData):

    def _packBlocks(self, eqCompDescr, _=None):
        return [formatters.packTitleDescBlock(backport.text(R.strings.epic_battle.abilityInfo.manage_abilities()), backport.text(R.strings.epic_battle.abilityInfo.manage_abilities_desc()))] if eqCompDescr == -1 else super(EpicSkillSlotTooltip, self)._packBlocks(_equipmentToEpicSkillConverter(self._epicMetaGameCtrl, eqCompDescr), None)


class EpicSkillSlotSetupInfoTooltip(BlocksTooltipData):
    _epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(EpicSkillSlotSetupInfoTooltip, self).__init__(ctx, TOOLTIP_TYPE.EPIC_SKILL_INFO)
        self._setWidth(_SETUP_INFO_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, vehicleCD=None):
        items = super(EpicSkillSlotSetupInfoTooltip, self)._packBlocks()
        vehicle = g_currentVehicle.item
        vType = replaceHyphenToUnderscore(vehicle.type if vehicle else VEHICLE_CLASS_NAME.HEAVY_TANK)
        resourceID = R.strings.epic_battle.tooltips.slotSetupInfo
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(resourceID.title.dyn(vType)())), desc=text_styles.main(backport.text(resourceID.subtitle())), img=backport.image(R.images.gui.maps.icons.vehicleTypes.large.dyn(vType)()), imgPadding=formatters.packPadding(left=-15, top=-10), txtOffset=56, padding=formatters.packPadding(top=5, bottom=-5)))
        blocks = []
        blocks.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(resourceID.scheme())), padding=formatters.packPadding(left=58, bottom=20)))
        blocks.append(formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.epicBattles.tooltips.battleAbility.dyn(vType)()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        items.append(formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(bottom=10)))
        blocks = []
        desc = text_styles.neutral(backport.text(resourceID.open.title(), desc=text_styles.main(backport.text(resourceID.open.desc()))))
        blocks.append(formatters.packImageTextBlockData(desc=desc, img=backport.image(R.images.gui.maps.icons.epicBattles.tooltips.battleAbility.open()), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, txtOffset=20, imgPadding=formatters.packPadding(top=-10, left=-10), padding=formatters.packPadding(top=4)))
        desc = text_styles.neutral(backport.text(resourceID.upgrade.title(), desc=text_styles.main(backport.text(resourceID.upgrade.desc()))))
        blocks.append(formatters.packImageTextBlockData(desc=desc, img=backport.image(R.images.gui.maps.icons.epicBattles.tooltips.battleAbility.upgrade()), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, txtOffset=20, imgPadding=formatters.packPadding(top=-10, left=-10), padding=formatters.packPadding(top=0)))
        items.append(formatters.packBuildUpBlockData(blocks))
        return items
