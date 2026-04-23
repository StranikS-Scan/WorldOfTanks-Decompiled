# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/artefact_scanning.py
from frameworks.wulf import ViewModel

class ArtefactScanning(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ArtefactScanning, self).__init__(properties=properties, commands=commands)

    def getTimeLeft(self):
        return self._getNumber(0)

    def setTimeLeft(self, value):
        self._setNumber(0, value)

    def getTotalTime(self):
        return self._getNumber(1)

    def setTotalTime(self, value):
        self._setNumber(1, value)

    def getActivePlayers(self):
        return self._getNumber(2)

    def setActivePlayers(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ArtefactScanning, self)._initialize()
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('totalTime', 0)
        self._addNumberProperty('activePlayers', 0)
