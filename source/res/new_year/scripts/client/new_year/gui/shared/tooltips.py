# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/tooltips.py
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from new_year.gui.impl.lobby.new_year.tooltips.ny_total_bonus_tooltip import NyTotalBonusTooltip

class NYCreditBonusTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(NYCreditBonusTooltipWindowData, self).__init__(context, TOOLTIP_TYPE.NY_CREDIT_BONUS)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(NyTotalBonusTooltip(), useDecorator=False)


class NewYearFillers(BlocksTooltipData):

    def __init__(self, context):
        super(NewYearFillers, self).__init__(context, None)
        self._setWidth(365)
        self._setContentMargin(0, 0, 0, 0)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(NewYearFillers, self)._packBlocks(*args, **kwargs)
        blocks = [formatters.packImageBlockData(backport.image(R.images.new_year.gui.maps.icons.newYear.infotype.icon_filler())), formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.ny.fillersTooltip.header())), padding=formatters.packPadding(-364, 30, 0, 30)), formatters.packTextBlockData(text_styles.mainBig(backport.text(R.strings.ny.fillersTooltip.description())), padding=formatters.packPadding(240, 30, 30, 30))]
        items.append(formatters.packBuildUpBlockData(blocks=blocks))
        return items
