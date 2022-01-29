# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/envelope_award_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class PlayerStatus(IntEnum):
    ISFRIEND = 0
    NOTFRIEND = 1
    FRIENDREQUESTINPROGRESS = 2


class EnvelopeAwardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EnvelopeAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getSenderID(self):
        return self._getNumber(0)

    def setSenderID(self, value):
        self._setNumber(0, value)

    def getSenderName(self):
        return self._getString(1)

    def setSenderName(self, value):
        self._setString(1, value)

    def getSenderStatus(self):
        return PlayerStatus(self._getNumber(2))

    def setSenderStatus(self, value):
        self._setNumber(2, value.value)

    def getWishID(self):
        return self._getNumber(3)

    def setWishID(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(EnvelopeAwardViewModel, self)._initialize()
        self._addNumberProperty('senderID', 0)
        self._addStringProperty('senderName', '')
        self._addNumberProperty('senderStatus')
        self._addNumberProperty('wishID', 0)
