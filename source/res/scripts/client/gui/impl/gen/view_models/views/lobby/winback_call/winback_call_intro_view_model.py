# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_intro_view_model.py
from frameworks.wulf import ViewModel

class WinbackCallIntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(WinbackCallIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getEventStart(self):
        return self._getNumber(0)

    def setEventStart(self, value):
        self._setNumber(0, value)

    def getEventFinish(self):
        return self._getNumber(1)

    def setEventFinish(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WinbackCallIntroViewModel, self)._initialize()
        self._addNumberProperty('eventStart', 0)
        self._addNumberProperty('eventFinish', 0)
        self.onClose = self._addCommand('onClose')
