# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/post_progression_tooltip_model.py
from frameworks.wulf import ViewModel

class PostProgressionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PostProgressionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBookXp(self):
        return self._getNumber(0)

    def setBookXp(self, value):
        self._setNumber(0, value)

    def getProgressCurrent(self):
        return self._getNumber(1)

    def setProgressCurrent(self, value):
        self._setNumber(1, value)

    def getProgressMax(self):
        return self._getNumber(2)

    def setProgressMax(self, value):
        self._setNumber(2, value)

    def getHasWarning(self):
        return self._getBool(3)

    def setHasWarning(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PostProgressionTooltipModel, self)._initialize()
        self._addNumberProperty('bookXp', 0)
        self._addNumberProperty('progressCurrent', 0)
        self._addNumberProperty('progressMax', 0)
        self._addBoolProperty('hasWarning', False)
