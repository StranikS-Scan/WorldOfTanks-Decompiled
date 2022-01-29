# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/main_view/store_envelopes/store_envelopes_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.store_envelopes.received_envelope_model import ReceivedEnvelopeModel

class EnvelopeType(IntEnum):
    PREMIUMPAID = 0
    PAID = 1
    FREE = 2


class StoreEnvelopesModel(ViewModel):
    __slots__ = ('onChangeEnvelopeType', 'onOpenHistoryView', 'onOpenEnvelopesByID', 'onOpenEnvelopes', 'onSetPageIndex')

    def __init__(self, properties=9, commands=5):
        super(StoreEnvelopesModel, self).__init__(properties=properties, commands=commands)

    def getInitialSenderID(self):
        return self._getNumber(0)

    def setInitialSenderID(self, value):
        self._setNumber(0, value)

    def getCurrentEnvelopeType(self):
        return EnvelopeType(self._getNumber(1))

    def setCurrentEnvelopeType(self, value):
        self._setNumber(1, value.value)

    def getReceivedEnvelopes(self):
        return self._getArray(2)

    def setReceivedEnvelopes(self, value):
        self._setArray(2, value)

    def getFreeEnvelopesCount(self):
        return self._getNumber(3)

    def setFreeEnvelopesCount(self, value):
        self._setNumber(3, value)

    def getPaidEnvelopesCount(self):
        return self._getNumber(4)

    def setPaidEnvelopesCount(self, value):
        self._setNumber(4, value)

    def getPremiumPaidEnvelopesCount(self):
        return self._getNumber(5)

    def setPremiumPaidEnvelopesCount(self, value):
        self._setNumber(5, value)

    def getPageIndex(self):
        return self._getNumber(6)

    def setPageIndex(self, value):
        self._setNumber(6, value)

    def getPageCount(self):
        return self._getNumber(7)

    def setPageCount(self, value):
        self._setNumber(7, value)

    def getIsOpeningFeatureEnabled(self):
        return self._getBool(8)

    def setIsOpeningFeatureEnabled(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(StoreEnvelopesModel, self)._initialize()
        self._addNumberProperty('initialSenderID', -1)
        self._addNumberProperty('currentEnvelopeType')
        self._addArrayProperty('receivedEnvelopes', Array())
        self._addNumberProperty('freeEnvelopesCount', 0)
        self._addNumberProperty('paidEnvelopesCount', 0)
        self._addNumberProperty('premiumPaidEnvelopesCount', 0)
        self._addNumberProperty('pageIndex', 0)
        self._addNumberProperty('pageCount', 0)
        self._addBoolProperty('isOpeningFeatureEnabled', True)
        self.onChangeEnvelopeType = self._addCommand('onChangeEnvelopeType')
        self.onOpenHistoryView = self._addCommand('onOpenHistoryView')
        self.onOpenEnvelopesByID = self._addCommand('onOpenEnvelopesByID')
        self.onOpenEnvelopes = self._addCommand('onOpenEnvelopes')
        self.onSetPageIndex = self._addCommand('onSetPageIndex')
