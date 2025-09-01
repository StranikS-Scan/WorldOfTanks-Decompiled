# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/info_page_model.py
from frameworks.wulf import ViewModel

class InfoPageModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(InfoPageModel, self).__init__(properties=properties, commands=commands)

    def getRerollInterval(self):
        return self._getNumber(0)

    def setRerollInterval(self, value):
        self._setNumber(0, value)

    def getIsWeeklySectionAvailable(self):
        return self._getBool(1)

    def setIsWeeklySectionAvailable(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(InfoPageModel, self)._initialize()
        self._addNumberProperty('rerollInterval', 0)
        self._addBoolProperty('isWeeklySectionAvailable', False)
        self.onClose = self._addCommand('onClose')
