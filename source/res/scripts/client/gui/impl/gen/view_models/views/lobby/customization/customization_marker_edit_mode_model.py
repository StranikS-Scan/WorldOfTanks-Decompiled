# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_marker_edit_mode_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class InscriptionStateEnum(IntEnum):
    EMPTY = 0
    SUBMITENTER = 1
    FIRSTENTER = 2
    EDITENTER = 3
    NOTAVAILABLEENTER = 4


class CustomizationMarkerEditModeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(CustomizationMarkerEditModeModel, self).__init__(properties=properties, commands=commands)

    def getEditDigitsCount(self):
        return self._getNumber(0)

    def setEditDigitsCount(self, value):
        self._setNumber(0, value)

    def getInscriptionState(self):
        return InscriptionStateEnum(self._getNumber(1))

    def setInscriptionState(self, value):
        self._setNumber(1, value.value)

    def getInvalidInscriptionNumber(self):
        return self._getString(2)

    def setInvalidInscriptionNumber(self, value):
        self._setString(2, value)

    def getInscriptionFirstEnterRange(self):
        return self._getArray(3)

    def setInscriptionFirstEnterRange(self, value):
        self._setArray(3, value)

    @staticmethod
    def getInscriptionFirstEnterRangeType():
        return unicode

    def getInscriptionDelay(self):
        return self._getNumber(4)

    def setInscriptionDelay(self, value):
        self._setNumber(4, value)

    def getInscriptionDuration(self):
        return self._getNumber(5)

    def setInscriptionDuration(self, value):
        self._setNumber(5, value)

    def getStartTimestamp(self):
        return self._getReal(6)

    def setStartTimestamp(self, value):
        self._setReal(6, value)

    def _initialize(self):
        super(CustomizationMarkerEditModeModel, self)._initialize()
        self._addNumberProperty('editDigitsCount', 0)
        self._addNumberProperty('inscriptionState')
        self._addStringProperty('invalidInscriptionNumber', '')
        self._addArrayProperty('inscriptionFirstEnterRange', Array())
        self._addNumberProperty('inscriptionDelay', 0)
        self._addNumberProperty('inscriptionDuration', 0)
        self._addRealProperty('startTimestamp', 0.0)
