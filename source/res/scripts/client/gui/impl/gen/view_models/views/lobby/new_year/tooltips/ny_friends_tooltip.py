# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_friends_tooltip.py
from frameworks.wulf import ViewModel

class NyFriendsTooltip(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyFriendsTooltip, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getPayload(self):
        return self._getString(1)

    def setPayload(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NyFriendsTooltip, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('payload', '')
