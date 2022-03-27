# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/trade_in.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getDueDateOrTimeStr
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips import formatters, TOOLTIP_TYPE, ToolTipBaseData
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.server_events import IEventsCache

class TradeInInfoTooltipData(BlocksTooltipData):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(TradeInInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.TRADE_IN_INFO)
        self._setWidth(380)
        self._setContentMargin(right=62)

    def _packBlocks(self, *args, **kwargs):
        return [formatters.packBuildUpBlockData(blocks=self.__getHeader(), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL), formatters.packBuildUpBlockData(blocks=self.__getInfo(), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE), formatters.packBuildUpBlockData(blocks=self.__getFooter(), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL)]

    @staticmethod
    def __getHeader():
        return [formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.tradeIn.trade_in_icon()), title=text_styles.highTitle(backport.text(R.strings.tooltips.tradeInInfo.header())), imgPadding=formatters.packPadding(left=2, top=4), txtPadding=formatters.packPadding(left=14, top=12))]

    @staticmethod
    def __getInfo():
        offerText = backport.text(R.strings.tooltips.tradeInInfo.tradeOffOffer())
        return [formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.prem_small_icon()), imgPadding=formatters.packPadding(top=4), title=text_styles.main(offerText), txtPadding=formatters.packPadding(left=3), padding=formatters.packPadding(left=62, bottom=18)), formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.discount()), imgPadding=formatters.packPadding(top=-1), title=text_styles.main(backport.text(R.strings.tooltips.tradeInInfo.discount())), padding=formatters.packPadding(left=60))]

    @staticmethod
    def __getFooter():
        return [formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.tradeInInfo.actionTime())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(left=34)), formatters.packAlignedTextBlockData(text=text_styles.neutral(_withTradeInUntil()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(left=34))]


class TradeInInfoNotAvailableData(ToolTipBaseData):
    __tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, context):
        super(TradeInInfoNotAvailableData, self).__init__(context, TOOLTIP_TYPE.TRADE_IN_INFO_NOT_AVAILABLE)

    def getDisplayableData(self, *args, **kwargs):
        if not self.__tradeIn.isEnabled():
            header = backport.text(R.strings.tooltips.tradeInExpired.header())
            body = backport.text(R.strings.tooltips.tradeInExpired.body())
        else:
            header = backport.text(R.strings.tooltips.tradeInNoVehicles.header())
            body = backport.text(R.strings.tooltips.tradeInNoVehicles.body()).format(range=_withTradeInUntil())
        return {'header': header,
         'body': body}


class TradeInStateNotAvailableData(ToolTipBaseData):

    def __init__(self, context):
        super(TradeInStateNotAvailableData, self).__init__(context, TOOLTIP_TYPE.TRADE_IN_STATE_NOT_AVAILABLE)

    def getDisplayableData(self, *args, **kwargs):
        vehicle = args[0]
        state = vehicle.getState()[0] if vehicle is not None else Vehicle.VEHICLE_STATE.UNDAMAGED
        if vehicle is not None and state in Vehicle.TRADE_OFF_NOT_READY_STATES:
            vehicleDamagedStates = (Vehicle.VEHICLE_STATE.DESTROYED, Vehicle.VEHICLE_STATE.EXPLODED, Vehicle.VEHICLE_STATE.DAMAGED)
            if state in vehicleDamagedStates:
                state = Vehicle.VEHICLE_STATE.DAMAGED
            body = backport.text(R.strings.tooltips.tradeInUnavailable.dyn(state)())
        else:
            body = backport.text(R.strings.tooltips.tradeInUnavailable.body())
        return {'header': backport.text(R.strings.tooltips.tradeInUnavailable.header()),
         'body': body}


@dependency.replace_none_kwargs(tradeIn=ITradeInController)
def _withTradeInUntil(tradeIn=None):
    endTimestamp = tradeIn.getExpirationTime()
    return backport.text(R.strings.menu.dateTime.trade_in.undefined()) if endTimestamp == 0 else getDueDateOrTimeStr(endTimestamp)
