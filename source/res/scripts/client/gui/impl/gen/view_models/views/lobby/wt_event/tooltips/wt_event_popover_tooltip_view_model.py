# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_popover_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.infotype_slot_model import InfotypeSlotModel

class BoxType(Enum):
    WTHUNTER = 'wt_hunter'
    WTBOSS = 'wt_boss'


class WtEventPopoverTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WtEventPopoverTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getGuaranteedLimit(self):
        return self._getNumber(0)

    def setGuaranteedLimit(self, value):
        self._setNumber(0, value)

    def getBoxType(self):
        return BoxType(self._getString(1))

    def setBoxType(self, value):
        self._setString(1, value.value)

    def getSlots(self):
        return self._getArray(2)

    def setSlots(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSlotsType():
        return InfotypeSlotModel

    def _initialize(self):
        super(WtEventPopoverTooltipViewModel, self)._initialize()
        self._addNumberProperty('guaranteedLimit', 0)
        self._addStringProperty('boxType')
        self._addArrayProperty('slots', Array())
