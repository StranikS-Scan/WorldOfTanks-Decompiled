# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pre_launch/pre_launch_view_model.py
from frameworks.wulf import ViewModel

class PreLaunchViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PreLaunchViewModel, self).__init__(properties=properties, commands=commands)

    def getProgress(self):
        return self._getNumber(0)

    def setProgress(self, value):
        self._setNumber(0, value)

    def getTiser(self):
        return self._getString(1)

    def setTiser(self, value):
        self._setString(1, value)

    def getIsTeaserHidden(self):
        return self._getBool(2)

    def setIsTeaserHidden(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PreLaunchViewModel, self)._initialize()
        self._addNumberProperty('progress', 0)
        self._addStringProperty('tiser', '')
        self._addBoolProperty('isTeaserHidden', False)
