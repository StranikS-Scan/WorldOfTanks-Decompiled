# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/parallax_view_model.py
from frameworks.wulf import ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.parallax_model import ParallaxModel

class ParallaxViewModel(ViewModel):
    __slots__ = ('onSlide',)

    def __init__(self, properties=2, commands=1):
        super(ParallaxViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def parallax(self):
        return self._getViewModel(0)

    @staticmethod
    def getParallaxType():
        return ParallaxModel

    def getIsParallaxEnabled(self):
        return self._getBool(1)

    def setIsParallaxEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ParallaxViewModel, self)._initialize()
        self._addViewModelProperty('parallax', ParallaxModel())
        self._addBoolProperty('isParallaxEnabled', False)
        self.onSlide = self._addCommand('onSlide')
