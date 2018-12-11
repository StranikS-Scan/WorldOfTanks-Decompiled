# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/ny_widget_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class NyWidgetModel(ViewModel):
    __slots__ = ()
    WIDGET_NO_ANIM = 0
    WIDGET_NORMAL_ANIM = 1
    WIDGET_LVLUP_ANIM = 2
    WIDGET_LVLDOWN_ANIM = 3

    def getWidgetAnim(self):
        return self._getNumber(0)

    def setWidgetAnim(self, value):
        self._setNumber(0, value)

    def getProgress(self):
        return self._getReal(1)

    def setProgress(self, value):
        self._setReal(1, value)

    def getIconSrc(self):
        return self._getResource(2)

    def setIconSrc(self, value):
        self._setResource(2, value)

    def getPrevIconSrc(self):
        return self._getResource(3)

    def setPrevIconSrc(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(NyWidgetModel, self)._initialize()
        self._addNumberProperty('widgetAnim', 0)
        self._addRealProperty('progress', 0.0)
        self._addResourceProperty('iconSrc', Resource.INVALID)
        self._addResourceProperty('prevIconSrc', Resource.INVALID)
