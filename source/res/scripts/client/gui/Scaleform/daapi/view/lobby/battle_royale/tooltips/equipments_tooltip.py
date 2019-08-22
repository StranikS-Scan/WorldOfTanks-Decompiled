# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/equipments_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from items import vehicles, EQUIPMENT_TYPES
_TOOLTIP_WIDTH = 420

class EquipmentsTooltipData(BlocksTooltipData):

    def __init__(self, context=None):
        super(EquipmentsTooltipData, self).__init__(context, TOOLTIP_TYPE.MODULE)
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        module = vehicles.g_cache.equipments()[args[0]]
        if module is None:
            return
        else:
            items = super(EquipmentsTooltipData, self)._packBlocks()
            leftPadding = 20
            rightPadding = 20
            topPadding = 20
            verticalPadding = 2
            innerBlockLeftPadding = 100
            headerBlockItem = [formatters.packBuildUpBlockData(self.__constructHeaderBlock(module, leftPadding, innerBlockLeftPadding), padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding, bottom=verticalPadding))]
            cooldownBlock = self.__constructCooldownBlock(module, verticalPadding, innerBlockLeftPadding)
            if cooldownBlock is not None:
                headerBlockItem.append(cooldownBlock)
            items.append(formatters.packBuildUpBlockData(headerBlockItem))
            items.append(formatters.packBuildUpBlockData(self.__constructDescriptionBlock(module, leftPadding), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=verticalPadding, bottom=verticalPadding)))
            items.append(formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.battle_royale.artefact.source())), padding=formatters.packPadding(left=innerBlockLeftPadding, top=verticalPadding)))
            return items

    @staticmethod
    def __constructHeaderBlock(module, leftPadding, innerBlockLeftPadding):
        block = []
        block.append(formatters.packImageTextBlockData(title=text_styles.highTitle(module.userString), desc=text_styles.main(backport.text(R.strings.tooltips.battle_royale.artefact.limit())), img=backport.image(R.images.gui.maps.icons.battleRoyale.artefact.dyn(module.iconName)()), imgPadding=formatters.packPadding(left=7), txtGap=-4, txtOffset=innerBlockLeftPadding - leftPadding))
        return block

    @staticmethod
    def __constructCooldownBlock(module, verticalPadding, innerBlockLeftPadding):
        cooldownSeconds = EquipmentsTooltipData.__getCooldownTime(module)
        return formatters.packTextBlockData(text=' '.join([text_styles.stats(int(cooldownSeconds)),
         '  ',
         text_styles.main(backport.text(R.strings.menu.moduleInfo.params.cooldownSeconds())),
         text_styles.standard(backport.text(R.strings.menu.tank_params.s()))]), padding=formatters.packPadding(bottom=verticalPadding, left=innerBlockLeftPadding)) if cooldownSeconds > 0 else None

    @staticmethod
    def __getCooldownTime(item):
        if item.equipmentType == EQUIPMENT_TYPES.regular:
            return item.cooldownSeconds
        return item.cooldownTime if item.equipmentType == EQUIPMENT_TYPES.battleAbilities else 0

    @staticmethod
    def __constructDescriptionBlock(item, leftPadding):
        block = []
        block.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.equipment.onUse())), desc=text_styles.main(EquipmentsTooltipData.__getDescription(item)), padding=formatters.packPadding(top=2, left=101 - leftPadding), descPadding=formatters.packPadding(bottom=-10)))
        return block

    @staticmethod
    def __getDescription(item):
        descr = ''
        if item.equipmentType == EQUIPMENT_TYPES.regular:
            descr = item.longDescriptionSpecial
        elif item.equipmentType == EQUIPMENT_TYPES.battleAbilities:
            descr = item.getDescription()
        return descr
