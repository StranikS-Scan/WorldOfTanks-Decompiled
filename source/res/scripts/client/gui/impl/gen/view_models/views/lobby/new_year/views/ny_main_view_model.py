# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_main_view_model.py
from frameworks.wulf import ViewModel

class NyMainViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(NyMainViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentViewResId(self):
        return self._getNumber(0)

    def setCurrentViewResId(self, value):
        self._setNumber(0, value)

    def getNextViewResId(self):
        return self._getNumber(1)

    def setNextViewResId(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyMainViewModel, self)._initialize()
        self._addNumberProperty('currentViewResId', 0)
        self._addNumberProperty('nextViewResId', 0)
        self.onClose = self._addCommand('onClose')
