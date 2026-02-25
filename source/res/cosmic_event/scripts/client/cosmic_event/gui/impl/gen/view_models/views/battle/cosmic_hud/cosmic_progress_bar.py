# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/cosmic_progress_bar.py
from enum import Enum
from frameworks.wulf import ViewModel

class ProgressBarType(Enum):
    CORAL = 'coral'
    ARTIFACT_ZONE = 'artifactZone'


class CosmicProgressBar(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CosmicProgressBar, self).__init__(properties=properties, commands=commands)

    def getBarType(self):
        return ProgressBarType(self._getString(0))

    def setBarType(self, value):
        self._setString(0, value.value)

    def getTimeLeft(self):
        return self._getNumber(1)

    def setTimeLeft(self, value):
        self._setNumber(1, value)

    def getTotalTime(self):
        return self._getNumber(2)

    def setTotalTime(self, value):
        self._setNumber(2, value)

    def getActivePlayers(self):
        return self._getNumber(3)

    def setActivePlayers(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(CosmicProgressBar, self)._initialize()
        self._addStringProperty('barType')
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('totalTime', 0)
        self._addNumberProperty('activePlayers', 0)
