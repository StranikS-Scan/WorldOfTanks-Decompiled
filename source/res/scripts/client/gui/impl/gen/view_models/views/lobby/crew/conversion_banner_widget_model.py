# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/conversion_banner_widget_model.py
from frameworks.wulf import ViewModel

class ConversionBannerWidgetModel(ViewModel):
    __slots__ = ('onStartConversion',)

    def __init__(self, properties=2, commands=1):
        super(ConversionBannerWidgetModel, self).__init__(properties=properties, commands=commands)

    def getSecondsLeft(self):
        return self._getNumber(0)

    def setSecondsLeft(self, value):
        self._setNumber(0, value)

    def getIsDisabled(self):
        return self._getBool(1)

    def setIsDisabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ConversionBannerWidgetModel, self)._initialize()
        self._addNumberProperty('secondsLeft', 0)
        self._addBoolProperty('isDisabled', False)
        self.onStartConversion = self._addCommand('onStartConversion')
