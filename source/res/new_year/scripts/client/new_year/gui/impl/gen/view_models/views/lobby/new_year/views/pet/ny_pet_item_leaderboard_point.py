# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/ny_pet_item_leaderboard_point.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import NyIndicatorType

class NyPetItemLeaderboardPoint(NyIndicatorType):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyPetItemLeaderboardPoint, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyPetItemLeaderboardPoint, self)._initialize()
        self._addNumberProperty('value', 0)
        self._addNumberProperty('id', 0)
