# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/help_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.help_slide_view_model import HelpSlideViewModel

class HelpViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(HelpViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedSlideIndex(self):
        return self._getNumber(0)

    def setSelectedSlideIndex(self, value):
        self._setNumber(0, value)

    def getSlides(self):
        return self._getArray(1)

    def setSlides(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSlidesType():
        return HelpSlideViewModel

    def _initialize(self):
        super(HelpViewModel, self)._initialize()
        self._addNumberProperty('selectedSlideIndex', 0)
        self._addArrayProperty('slides', Array())
        self.onClose = self._addCommand('onClose')
