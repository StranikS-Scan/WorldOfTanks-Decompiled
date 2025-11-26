# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/stronghold_event/stronghold_event_banner_tooltip_view_model.py
from frameworks.wulf import ViewModel

class StrongholdEventBannerTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(StrongholdEventBannerTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(StrongholdEventBannerTooltipViewModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
