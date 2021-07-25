# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_queue_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MapsTrainingQueueModel(ViewModel):
    __slots__ = ('onQuit', 'onMenu', 'onShowPrevTip', 'onShowNextTip', 'onMoveSpace')
    DELAY_DEFAULT = ''
    DELAY_NORMAL = 'normal'
    DELAY_LONG = 'long'

    def __init__(self, properties=4, commands=5):
        super(MapsTrainingQueueModel, self).__init__(properties=properties, commands=commands)

    def getTime(self):
        return self._getString(0)

    def setTime(self, value):
        self._setString(0, value)

    def getDescrTip(self):
        return self._getResource(1)

    def setDescrTip(self, value):
        self._setResource(1, value)

    def getIsDelay(self):
        return self._getBool(2)

    def setIsDelay(self, value):
        self._setBool(2, value)

    def getDelayStatus(self):
        return self._getString(3)

    def setDelayStatus(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(MapsTrainingQueueModel, self)._initialize()
        self._addStringProperty('time', '')
        self._addResourceProperty('descrTip', R.invalid())
        self._addBoolProperty('isDelay', False)
        self._addStringProperty('delayStatus', '')
        self.onQuit = self._addCommand('onQuit')
        self.onMenu = self._addCommand('onMenu')
        self.onShowPrevTip = self._addCommand('onShowPrevTip')
        self.onShowNextTip = self._addCommand('onShowNextTip')
        self.onMoveSpace = self._addCommand('onMoveSpace')
