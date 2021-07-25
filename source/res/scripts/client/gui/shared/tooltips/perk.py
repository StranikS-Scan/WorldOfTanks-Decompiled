# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/perk.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData

class PerkTTCTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(PerkTTCTooltipData, self).__init__(context, TOOLTIP_TYPE.PERK_TTC)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(445)

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        return [self.__packTitleBlock()]

    def __packTitleBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(self.item.name)), desc=text_styles.main(self.item.flashFormattedDescription), img=backport.image(R.images.gui.maps.icons.perks.normal.c_48x48.dyn(self.item.icon)()), imgPadding={'left': 0,
         'top': 3}, txtGap=-4, txtOffset=60, padding={'top': -1,
         'left': 7,
         'bottom': 10})
