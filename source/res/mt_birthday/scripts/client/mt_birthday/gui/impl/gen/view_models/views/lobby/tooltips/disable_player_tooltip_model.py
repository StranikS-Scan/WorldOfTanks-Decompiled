# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/disable_player_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class DisabledReason(Enum):
    NOTAVAILABLE = 'notAvailable'
    BANNED = 'banned'
    BOT = 'bot'
    BLACKLIST = 'blackList'


class DisablePlayerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DisablePlayerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTime(self):
        return self._getNumber(0)

    def setTime(self, value):
        self._setNumber(0, value)

    def getDisabledReason(self):
        return DisabledReason(self._getString(1))

    def setDisabledReason(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(DisablePlayerTooltipModel, self)._initialize()
        self._addNumberProperty('time', 0)
        self._addStringProperty('disabledReason')
