# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portal_availability.py
from frameworks.wulf import ViewModel

class WtEventPortalAvailability(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtEventPortalAvailability, self).__init__(properties=properties, commands=commands)

    def getAttemptPrice(self):
        return self._getNumber(0)

    def setAttemptPrice(self, value):
        self._setNumber(0, value)

    def getLootBoxesCount(self):
        return self._getNumber(1)

    def setLootBoxesCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WtEventPortalAvailability, self)._initialize()
        self._addNumberProperty('attemptPrice', 0)
        self._addNumberProperty('lootBoxesCount', 0)
