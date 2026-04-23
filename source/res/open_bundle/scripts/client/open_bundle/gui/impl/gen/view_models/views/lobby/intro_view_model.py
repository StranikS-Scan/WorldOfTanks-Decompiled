# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/gen/view_models/views/lobby/intro_view_model.py
from frameworks.wulf import ViewModel

class IntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onExternalLink')

    def __init__(self, properties=2, commands=2):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    def getBundleType(self):
        return self._getString(0)

    def setBundleType(self, value):
        self._setString(0, value)

    def getTimeLeft(self):
        return self._getNumber(1)

    def setTimeLeft(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self._addStringProperty('bundleType', '')
        self._addNumberProperty('timeLeft', 0)
        self.onClose = self._addCommand('onClose')
        self.onExternalLink = self._addCommand('onExternalLink')
