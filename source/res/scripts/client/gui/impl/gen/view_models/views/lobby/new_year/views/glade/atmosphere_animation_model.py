# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/atmosphere_animation_model.py
from frameworks.wulf import ViewModel

class AtmosphereAnimationModel(ViewModel):
    __slots__ = ('onAnimationEnd',)

    def __init__(self, properties=3, commands=1):
        super(AtmosphereAnimationModel, self).__init__(properties=properties, commands=commands)

    def getSlotId(self):
        return self._getNumber(0)

    def setSlotId(self, value):
        self._setNumber(0, value)

    def getPoints(self):
        return self._getNumber(1)

    def setPoints(self, value):
        self._setNumber(1, value)

    def getIsReady(self):
        return self._getBool(2)

    def setIsReady(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(AtmosphereAnimationModel, self)._initialize()
        self._addNumberProperty('slotId', 0)
        self._addNumberProperty('points', 0)
        self._addBoolProperty('isReady', False)
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
