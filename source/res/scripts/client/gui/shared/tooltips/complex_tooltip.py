# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/complex_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class ComplexTooltip(BlocksTooltipData):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, context, disableAnim):
        super(ComplexTooltip, self).__init__(context, None)
        self._setMargins(11, 14)
        self._setWidth(520)
        self._disableAnim = disableAnim
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(ComplexTooltip, self)._packBlocks(*args, **kwargs)
        tooltipText = args[0]
        tooltipText = tooltipText.split('<br/>')
        items.append(formatters.packImageTextBlockData(title=tooltipText[0], desc=tooltipText[1]))
        block = formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.lobby.iconBtnAlt()), txtOffset=40, padding=formatters.packPadding(bottom=-7, top=-5, left=20 - self._getContentMargin()['left']), desc=formatters.text_styles.main(backport.text(R.strings.tooltips.advanced.info())), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_ADVANCED_KEY_BLOCK_LINKAGE)
        block['data']['animated'] = not self._disableAnim
        items.append(block)
        return items
