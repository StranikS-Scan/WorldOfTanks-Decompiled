# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/fading_cover_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class FadingCoverViewModel(ViewModel):
    __slots__ = ('onFadingOutComplete', 'onFadingInComplete')

    def __init__(self, properties=4, commands=2):
        super(FadingCoverViewModel, self).__init__(properties=properties, commands=commands)

    def getBackground(self):
        return self._getResource(0)

    def setBackground(self, value):
        self._setResource(0, value)

    def getIsVisible(self):
        return self._getBool(1)

    def setIsVisible(self, value):
        self._setBool(1, value)

    def getFadeInDuration(self):
        return self._getReal(2)

    def setFadeInDuration(self, value):
        self._setReal(2, value)

    def getFadeOutDuration(self):
        return self._getReal(3)

    def setFadeOutDuration(self, value):
        self._setReal(3, value)

    def _initialize(self):
        super(FadingCoverViewModel, self)._initialize()
        self._addResourceProperty('background', R.invalid())
        self._addBoolProperty('isVisible', False)
        self._addRealProperty('fadeInDuration', 0.0)
        self._addRealProperty('fadeOutDuration', 0.0)
        self.onFadingOutComplete = self._addCommand('onFadingOutComplete')
        self.onFadingInComplete = self._addCommand('onFadingInComplete')
