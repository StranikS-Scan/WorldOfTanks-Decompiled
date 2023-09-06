# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/common/medal_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MedalTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MedalTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getImage(self):
        return self._getResource(1)

    def setImage(self, value):
        self._setResource(1, value)

    def getConditions(self):
        return self._getResource(2)

    def setConditions(self, value):
        self._setResource(2, value)

    def getDescription(self):
        return self._getResource(3)

    def setDescription(self, value):
        self._setResource(3, value)

    def _initialize(self):
        super(MedalTooltipViewModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('conditions', R.invalid())
        self._addResourceProperty('description', R.invalid())
