# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_opt_devices.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleOptDeviceTooltipData(BlocksTooltipData):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, context):
        super(BattleOptDeviceTooltipData, self).__init__(context, TOOLTIP_TYPE.EQUIPMENT)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(400)
        return

    def _packBlocks(self, itemCD, itemStatus):
        items = super(BattleOptDeviceTooltipData, self)._packBlocks()
        _, _, deviceID = vehicles.parseIntCompactDescr(itemCD)
        itemInBattle = self.guiSessionProvider.shared.optionalDevices.getOptDeviceInBattle(deviceID)
        if not itemInBattle:
            return items
        descriptor = itemInBattle.getDescriptor()
        leftPadding = 20
        rightPadding = 20
        topPadding = 20
        battleDescr = R.strings.artefacts.dyn(descriptor.groupName).battle_descr
        if battleDescr:
            desc = backport.text(battleDescr())
        else:
            desc = descriptor.shortDescriptionSpecial.format(colorTagOpen='', colorTagClose='')
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.artefacts.dyn(descriptor.tierlessName).name())), desc=text_styles.main(desc), padding=formatters.packPadding(bottom=-10))], padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=topPadding)))
        battleStatuses = itemInBattle.getBattleStatus()
        for ind, statusStr in enumerate(battleStatuses):
            items.append(formatters.packBuildUpBlockData([formatters.packAlignedTextBlockData(text=statusStr, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(bottom=-26 if ind + 1 != len(battleStatuses) else -10))]))

        return items
