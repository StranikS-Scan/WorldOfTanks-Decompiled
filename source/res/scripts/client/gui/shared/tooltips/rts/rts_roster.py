# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/rts/rts_roster.py
from typing import TYPE_CHECKING
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
if TYPE_CHECKING:
    from typing import List, Dict

class RtsVehicleRestrictionsTooltip(BlocksTooltipData):
    __titlePadding = formatters.packPadding(top=2)
    __descriptionPadding = formatters.packPadding(bottom=5)

    def __init__(self, context):
        super(RtsVehicleRestrictionsTooltip, self).__init__(context, None)
        self._setWidth(358)
        return

    def _packBlocks(self, restrictions):
        items = super(RtsVehicleRestrictionsTooltip, self)._packBlocks()
        title = text_styles.middleTitle(backport.text(R.strings.rts_battles.tooltip.supportedClasses.title()))
        items.append(formatters.packTextBlockData(title, padding=self.__titlePadding))
        descr = text_styles.main(backport.text(R.strings.rts_battles.tooltip.supportedClasses.descr()))
        items.append(formatters.packTextBlockData(descr, padding=self.__descriptionPadding))
        for restriction in restrictions:
            restriction = restriction.replace('-', '_')
            descr = text_styles.main(backport.text(R.strings.rts_battles.tooltip.supportedClasses.availableVehicleClasses.dyn(restriction)()))
            items.append(formatters.packTextBlockData(descr))

        return [formatters.packBuildUpBlockData(blocks=items)]
