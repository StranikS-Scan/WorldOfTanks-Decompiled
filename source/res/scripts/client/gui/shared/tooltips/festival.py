# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/festival.py
import logging
from gui.Scaleform.daapi.view.lobby.race.racing_vehicle_tooltip import RacingVehicleTooltipContent
from gui.Scaleform.daapi.view.lobby.race.racing_widget_cmp import RaceWidgetTooltip
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.lobby.tooltips.racing_cup_tooltip import RacingCupTooltip
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, ToolTipBaseData
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from items.components.festival_constants import FEST_ITEM_TYPE
_logger = logging.getLogger(__name__)

class FestivalTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(FestivalTooltipData, self).__init__(context, TOOLTIP_TYPE.FESTIVAL_ITEMS)
        self._setMargins(afterBlock=10, afterSeparator=10)
        self._setContentMargin(top=18, left=18, right=13)
        self._setWidth(320)
        self.__itemCD = None
        self.__itemData = None
        self._items = None
        return

    def _packBlocks(self, itemID, count=None, showStatus=True):
        self.__itemCD = itemID
        self._items = super(FestivalTooltipData, self)._packBlocks(itemID)
        self.__itemData = self.context.getFestivalItemData(itemID)
        showIcon = True
        isAlternative = self.__itemData.isAlternative()
        itemType = self.__itemData.getType()
        title = backport.text(self.__itemData.getNameResID())
        subtitle = backport.text(self.__itemData.getTypeResID())
        body = None
        descAccessor = self.__itemData.getDescription()
        if descAccessor.exists():
            body = backport.text(descAccessor())
        itemCost = self.__itemData.getCost()
        if itemType == FEST_ITEM_TYPE.RANK:
            showIcon = False
            isAlternative = False
            showStatus = False
        mainBlock = []
        mainBlock.append(formatters.packImageTextBlockData(title=text_styles.highTitle(title), desc=text_styles.standard(subtitle), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT))
        if showIcon:
            iconBlocks = []
            iconWidth = 312
            iconHeight = 187
            if itemType != FEST_ITEM_TYPE.BASIS:
                iconBlocks.append(formatters.packImageBlockData(img=backport.image(self.__itemData.getBasisResID()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=iconWidth, height=iconHeight))
            iconBlocks.append(formatters.packImageBlockData(img=backport.image(self.__itemData.getIconResID(useDefault=True)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=iconWidth, height=iconHeight))
            mainBlock.append(formatters.packBuildUpBlockData(blocks=iconBlocks, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, gap=-iconWidth, padding=formatters.packPadding(top=5, left=12)))
        if body is not None:
            mainBlock.append(formatters.packAlignedTextBlockData(text=text_styles.main(body), align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=5)))
        if isAlternative:
            mainBlock.append(formatters.packImageTextBlockData(ignoreImageSize=True, title=text_styles.middleTitle(backport.text(R.strings.festival.tooltip.item.alternative.title())), desc=text_styles.main(backport.text(R.strings.festival.tooltip.item.alternative.description())), img=backport.image(R.images.gui.maps.icons.festival.special_star()), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, imgPadding=formatters.packPadding(top=-43, left=-39, right=-38, bottom=-60), padding=formatters.packPadding(top=15, bottom=20)))
        self._items.append(formatters.packBuildUpBlockData(blocks=mainBlock, gap=5))
        if showStatus:
            if self.__itemData.isInInventory():
                self._items.append(formatters.packBuildUpBlockData(blocks=[formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.festival.items.item_recieved()), padding=formatters.packPadding(top=-14, bottom=-17)), formatters.packTextBlockData(text=text_styles.bonusAppliedText(backport.text(R.strings.festival.tooltip.status.received())), cutWidth=True, padding=formatters.packPadding(left=-10))], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=5), blockWidth=290))
            elif itemCost < 0:
                self._items.append(formatters.packBuildUpBlockData(blocks=[formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.festival.items.item_locked()), padding=formatters.packPadding(top=-12, bottom=-17)), formatters.packTextBlockData(text=text_styles.vehicleStatusCriticalTextSmall(backport.text(self.__itemData.getLockedTextResID())), cutWidth=True, padding=formatters.packPadding(left=-10))], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=5), blockWidth=290))
            else:
                self._items.append(formatters.packAlignedTextBlockData(text_styles.concatStylesWithSpace(text_styles.main(backport.text(R.strings.festival.tooltip.status.buy())), text_styles.expTextBig(itemCost), icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.festival.tickets()), width=24, height=24, vSpace=-6, hSpace=3)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-3, bottom=-1)))
        return self._items


class RaceVehicleTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(RaceVehicleTooltipWindowData, self).__init__(context, TOOLTIP_TYPE.RACE_VEHICLE)

    def getDisplayableData(self, intCD):
        return RacingVehicleTooltipContent(intCD)


class RaceWidgetTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(RaceWidgetTooltipWindowData, self).__init__(context, TOOLTIP_TYPE.RACE_WIDGET)

    def getDisplayableData(self):
        return RaceWidgetTooltip()


class RacingCupTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(RacingCupTooltipWindowData, self).__init__(context, TOOLTIP_TYPE.RACING_CUP)

    def getDisplayableData(self, cupType):
        return RacingCupTooltip(cupType)
