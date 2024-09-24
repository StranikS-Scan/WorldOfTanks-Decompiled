# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/entry_point_tooltip_view_model.py
from frameworks.wulf import ViewModel

class EntryPointTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EntryPointTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getEventExpireTime(self):
        return self._getNumber(2)

    def setEventExpireTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(EntryPointTooltipViewModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addBoolProperty('isEnabled', False)
        self._addNumberProperty('eventExpireTime', 0)
