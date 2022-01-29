# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/tooltips/envelope_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class EnvelopeType(IntEnum):
    PREMIUMPAID = 0
    PAID = 1
    FREE = 2


class EnvelopeTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(EnvelopeTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEnvelopeType(self):
        return EnvelopeType(self._getNumber(0))

    def setEnvelopeType(self, value):
        self._setNumber(0, value.value)

    def getEnvelopesCount(self):
        return self._getNumber(1)

    def setEnvelopesCount(self, value):
        self._setNumber(1, value)

    def getRareCharmsProbability(self):
        return self._getNumber(2)

    def setRareCharmsProbability(self, value):
        self._setNumber(2, value)

    def getHasSentEnvelope(self):
        return self._getBool(3)

    def setHasSentEnvelope(self, value):
        self._setBool(3, value)

    def getSecretSantaSentLimitTime(self):
        return self._getNumber(4)

    def setSecretSantaSentLimitTime(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(EnvelopeTooltipModel, self)._initialize()
        self._addNumberProperty('envelopeType')
        self._addNumberProperty('envelopesCount', 0)
        self._addNumberProperty('rareCharmsProbability', 0)
        self._addBoolProperty('hasSentEnvelope', False)
        self._addNumberProperty('secretSantaSentLimitTime', 0)
