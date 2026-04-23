# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/narration_view_model.py
from frameworks.wulf import ViewModel

class NarrationViewModel(ViewModel):
    __slots__ = ('onClose', 'onSlide', 'onVoiceoverToggle')

    def __init__(self, properties=4, commands=3):
        super(NarrationViewModel, self).__init__(properties=properties, commands=commands)

    def getSlideNumber(self):
        return self._getNumber(0)

    def setSlideNumber(self, value):
        self._setNumber(0, value)

    def getIsNextDisabled(self):
        return self._getBool(1)

    def setIsNextDisabled(self, value):
        self._setBool(1, value)

    def getIsPrevDisabled(self):
        return self._getBool(2)

    def setIsPrevDisabled(self, value):
        self._setBool(2, value)

    def getIsVoiceoverActive(self):
        return self._getBool(3)

    def setIsVoiceoverActive(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NarrationViewModel, self)._initialize()
        self._addNumberProperty('slideNumber', 0)
        self._addBoolProperty('isNextDisabled', False)
        self._addBoolProperty('isPrevDisabled', False)
        self._addBoolProperty('isVoiceoverActive', False)
        self.onClose = self._addCommand('onClose')
        self.onSlide = self._addCommand('onSlide')
        self.onVoiceoverToggle = self._addCommand('onVoiceoverToggle')
