# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_guest_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class GuestType(Enum):
    NY_DOG = 'ny_dog'
    NY_CAT = 'ny_cat'


class NyGuestTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyGuestTooltipModel, self).__init__(properties=properties, commands=commands)

    def getGuestType(self):
        return GuestType(self._getString(0))

    def setGuestType(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(NyGuestTooltipModel, self)._initialize()
        self._addStringProperty('guestType')
