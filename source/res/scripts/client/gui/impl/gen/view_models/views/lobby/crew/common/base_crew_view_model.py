# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/base_crew_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BaseCrewViewModel(ViewModel):
    __slots__ = ('onAbout', 'onClose', 'onBack', 'onHangar')

    def __init__(self, properties=2, commands=4):
        super(BaseCrewViewModel, self).__init__(properties=properties, commands=commands)

    def getBackButtonLabel(self):
        return self._getResource(0)

    def setBackButtonLabel(self, value):
        self._setResource(0, value)

    def getIsButtonBarVisible(self):
        return self._getBool(1)

    def setIsButtonBarVisible(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(BaseCrewViewModel, self)._initialize()
        self._addResourceProperty('backButtonLabel', R.invalid())
        self._addBoolProperty('isButtonBarVisible', True)
        self.onAbout = self._addCommand('onAbout')
        self.onClose = self._addCommand('onClose')
        self.onBack = self._addCommand('onBack')
        self.onHangar = self._addCommand('onHangar')
