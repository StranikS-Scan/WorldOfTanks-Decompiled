# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/main_view/info/info_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Link(IntEnum):
    LUNARRULES = 0
    ENVELOPESSHOP = 1
    INFOVIDEO = 2


class InfoModel(ViewModel):
    __slots__ = ('onLinkClick',)

    def __init__(self, properties=7, commands=1):
        super(InfoModel, self).__init__(properties=properties, commands=commands)

    def getEventStartTime(self):
        return self._getReal(0)

    def setEventStartTime(self, value):
        self._setReal(0, value)

    def getEventEndTime(self):
        return self._getReal(1)

    def setEventEndTime(self, value):
        self._setReal(1, value)

    def getSimpleCharmBonus(self):
        return self._getNumber(2)

    def setSimpleCharmBonus(self, value):
        self._setNumber(2, value)

    def getSpecialCharmSingleBonus(self):
        return self._getNumber(3)

    def setSpecialCharmSingleBonus(self, value):
        self._setNumber(3, value)

    def getSpecialCharmDoubleBonus(self):
        return self._getNumber(4)

    def setSpecialCharmDoubleBonus(self, value):
        self._setNumber(4, value)

    def getRareCharmsProbability(self):
        return self._getNumber(5)

    def setRareCharmsProbability(self, value):
        self._setNumber(5, value)

    def getSecretSantaSentLimitTime(self):
        return self._getNumber(6)

    def setSecretSantaSentLimitTime(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(InfoModel, self)._initialize()
        self._addRealProperty('eventStartTime', 0.0)
        self._addRealProperty('eventEndTime', 0.0)
        self._addNumberProperty('simpleCharmBonus', 0)
        self._addNumberProperty('specialCharmSingleBonus', 0)
        self._addNumberProperty('specialCharmDoubleBonus', 0)
        self._addNumberProperty('rareCharmsProbability', 0)
        self._addNumberProperty('secretSantaSentLimitTime', 0)
        self.onLinkClick = self._addCommand('onLinkClick')
