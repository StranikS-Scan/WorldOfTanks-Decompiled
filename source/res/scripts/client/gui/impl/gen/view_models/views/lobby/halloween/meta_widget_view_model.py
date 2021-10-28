# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/meta_widget_view_model.py
from frameworks.wulf import ViewModel

class MetaWidgetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MetaWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def getMaxProgress(self):
        return self._getNumber(1)

    def setMaxProgress(self, value):
        self._setNumber(1, value)

    def getNewVideoCount(self):
        return self._getNumber(2)

    def setNewVideoCount(self, value):
        self._setNumber(2, value)

    def getIsCompleted(self):
        return self._getBool(3)

    def setIsCompleted(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(MetaWidgetViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addNumberProperty('newVideoCount', 0)
        self._addBoolProperty('isCompleted', False)
