# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/integrated_auction/tooltips/auction_event_banner_tooltip_model.py
from frameworks.wulf import ViewModel

class AuctionEventBannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(AuctionEventBannerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsAvailable(self):
        return self._getBool(0)

    def setIsAvailable(self, value):
        self._setBool(0, value)

    def getTimerValue(self):
        return self._getNumber(1)

    def setTimerValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(AuctionEventBannerTooltipModel, self)._initialize()
        self._addBoolProperty('isAvailable', False)
        self._addNumberProperty('timerValue', 0)
