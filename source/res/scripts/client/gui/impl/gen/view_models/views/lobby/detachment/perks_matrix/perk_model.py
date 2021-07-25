# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/perks_matrix/perk_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel

class PerkModel(PerkShortModel):
    __slots__ = ()
    STATE_LOCKED = 'locked'
    STATE_OPENED = 'opened'

    def __init__(self, properties=17, commands=0):
        super(PerkModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(9)

    def setName(self, value):
        self._setResource(9, value)

    def getDescription(self):
        return self._getResource(10)

    def setDescription(self, value):
        self._setResource(10, value)

    def getMovie(self):
        return self._getString(11)

    def setMovie(self, value):
        self._setString(11, value)

    def getTempPoints(self):
        return self._getNumber(12)

    def setTempPoints(self, value):
        self._setNumber(12, value)

    def getMaxPoints(self):
        return self._getNumber(13)

    def setMaxPoints(self, value):
        self._setNumber(13, value)

    def getState(self):
        return self._getString(14)

    def setState(self, value):
        self._setString(14, value)

    def getIsRecommended(self):
        return self._getBool(15)

    def setIsRecommended(self, value):
        self._setBool(15, value)

    def getIsHighlightedByInstructor(self):
        return self._getBool(16)

    def setIsHighlightedByInstructor(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(PerkModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addStringProperty('movie', '')
        self._addNumberProperty('tempPoints', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addStringProperty('state', 'opened')
        self._addBoolProperty('isRecommended', False)
        self._addBoolProperty('isHighlightedByInstructor', False)
