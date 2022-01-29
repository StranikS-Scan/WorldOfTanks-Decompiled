# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/envelopes_history_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.player_envelopes_history import PlayerEnvelopesHistory

class EnvelopeTypes(IntEnum):
    PREMIUMPAID = 0
    PAID = 1
    FREE = 2


class ColumnType(IntEnum):
    PLAYERNAME = 1
    RECEIVEDENVELOPES = 2
    RECEIVEDGOLD = 3
    SENTINRESPONSE = 4


class ColumnSortingOrder(IntEnum):
    ASC = 0
    DESC = 1


class EnvelopesHistoryViewModel(ViewModel):
    __slots__ = ('onClose', 'onSendEnvelopeInResponse', 'onChangeEnvelopeTypeTab', 'onChangeCurrentPageNumber', 'onAddToFriends', 'onChangeColumnType', 'onGoToEnvelopeSend')

    def __init__(self, properties=11, commands=7):
        super(EnvelopesHistoryViewModel, self).__init__(properties=properties, commands=commands)

    def getEnvelopeTypeTab(self):
        return EnvelopeTypes(self._getNumber(0))

    def setEnvelopeTypeTab(self, value):
        self._setNumber(0, value.value)

    def getCurrentColumnSortingOrder(self):
        return ColumnSortingOrder(self._getNumber(1))

    def setCurrentColumnSortingOrder(self, value):
        self._setNumber(1, value.value)

    def getPlayersInfo(self):
        return self._getArray(2)

    def setPlayersInfo(self, value):
        self._setArray(2, value)

    def getCurrentPageNumber(self):
        return self._getNumber(3)

    def setCurrentPageNumber(self, value):
        self._setNumber(3, value)

    def getPagesNumber(self):
        return self._getNumber(4)

    def setPagesNumber(self, value):
        self._setNumber(4, value)

    def getPremiumPaidEnvelopesNumber(self):
        return self._getNumber(5)

    def setPremiumPaidEnvelopesNumber(self, value):
        self._setNumber(5, value)

    def getPaidEnvelopesNumber(self):
        return self._getNumber(6)

    def setPaidEnvelopesNumber(self, value):
        self._setNumber(6, value)

    def getFreeEnvelopesNumber(self):
        return self._getNumber(7)

    def setFreeEnvelopesNumber(self, value):
        self._setNumber(7, value)

    def getSelectedColumnType(self):
        return ColumnType(self._getNumber(8))

    def setSelectedColumnType(self, value):
        self._setNumber(8, value.value)

    def getIsGiftHistoryAvailable(self):
        return self._getBool(9)

    def setIsGiftHistoryAvailable(self, value):
        self._setBool(9, value)

    def getSyncInitiator(self):
        return self._getNumber(10)

    def setSyncInitiator(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(EnvelopesHistoryViewModel, self)._initialize()
        self._addNumberProperty('envelopeTypeTab')
        self._addNumberProperty('currentColumnSortingOrder')
        self._addArrayProperty('playersInfo', Array())
        self._addNumberProperty('currentPageNumber', 0)
        self._addNumberProperty('pagesNumber', 0)
        self._addNumberProperty('PremiumPaidEnvelopesNumber', 0)
        self._addNumberProperty('PaidEnvelopesNumber', 0)
        self._addNumberProperty('FreeEnvelopesNumber', 0)
        self._addNumberProperty('selectedColumnType')
        self._addBoolProperty('isGiftHistoryAvailable', True)
        self._addNumberProperty('syncInitiator', 0)
        self.onClose = self._addCommand('onClose')
        self.onSendEnvelopeInResponse = self._addCommand('onSendEnvelopeInResponse')
        self.onChangeEnvelopeTypeTab = self._addCommand('onChangeEnvelopeTypeTab')
        self.onChangeCurrentPageNumber = self._addCommand('onChangeCurrentPageNumber')
        self.onAddToFriends = self._addCommand('onAddToFriends')
        self.onChangeColumnType = self._addCommand('onChangeColumnType')
        self.onGoToEnvelopeSend = self._addCommand('onGoToEnvelopeSend')
