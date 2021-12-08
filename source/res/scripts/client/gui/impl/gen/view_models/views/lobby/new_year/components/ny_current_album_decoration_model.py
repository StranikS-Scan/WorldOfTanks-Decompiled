# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_current_album_decoration_model.py
from enum import IntEnum
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_album_decoration_model import NyAlbumDecorationModel

class MegaToyState(IntEnum):
    NOTRECEIVED = 0
    RECEIVED = 1
    INSTALLED = 2
    CRASHED = 3


class NyCurrentAlbumDecorationModel(NyAlbumDecorationModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(NyCurrentAlbumDecorationModel, self).__init__(properties=properties, commands=commands)

    def getBonusValue(self):
        return self._getReal(6)

    def setBonusValue(self, value):
        self._setReal(6, value)

    def getState(self):
        return MegaToyState(self._getNumber(7))

    def setState(self, value):
        self._setNumber(7, value.value)

    def getNewNumber(self):
        return self._getNumber(8)

    def setNewNumber(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(NyCurrentAlbumDecorationModel, self)._initialize()
        self._addRealProperty('bonusValue', 0.0)
        self._addNumberProperty('state')
        self._addNumberProperty('newNumber', 0)
