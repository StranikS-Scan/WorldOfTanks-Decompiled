# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/sub_mode_selector_view/sub_mode_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import RtsCurrencyViewModel

class SubModeStatus(Enum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    FREE = 'free'
    LOCKED = 'locked'


class SubModeTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(SubModeTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def currency(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getSectionTitle(self):
        return self._getString(3)

    def setSectionTitle(self, value):
        self._setString(3, value)

    def getSectionText(self):
        return self._getString(4)

    def setSectionText(self, value):
        self._setString(4, value)

    def getStatus(self):
        return SubModeStatus(self._getString(5))

    def setStatus(self, value):
        self._setString(5, value.value)

    def getUnavailableReason(self):
        return self._getString(6)

    def setUnavailableReason(self, value):
        self._setString(6, value)

    def getDate(self):
        return self._getNumber(7)

    def setDate(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(SubModeTooltipModel, self)._initialize()
        self._addViewModelProperty('currency', RtsCurrencyViewModel())
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('sectionTitle', '')
        self._addStringProperty('sectionText', '')
        self._addStringProperty('status')
        self._addStringProperty('unavailableReason', '')
        self._addNumberProperty('date', 0)
