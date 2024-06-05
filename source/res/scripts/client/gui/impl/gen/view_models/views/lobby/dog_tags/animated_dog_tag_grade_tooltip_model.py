# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/animated_dog_tag_grade_tooltip_model.py
from frameworks.wulf import ViewModel

class AnimatedDogTagGradeTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AnimatedDogTagGradeTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEngravingId(self):
        return self._getNumber(0)

    def setEngravingId(self, value):
        self._setNumber(0, value)

    def getBackgroundId(self):
        return self._getNumber(1)

    def setBackgroundId(self, value):
        self._setNumber(1, value)

    def getStage(self):
        return self._getNumber(2)

    def setStage(self, value):
        self._setNumber(2, value)

    def getRequiredItemsCount(self):
        return self._getNumber(3)

    def setRequiredItemsCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(AnimatedDogTagGradeTooltipModel, self)._initialize()
        self._addNumberProperty('engravingId', 0)
        self._addNumberProperty('backgroundId', 0)
        self._addNumberProperty('stage', 0)
        self._addNumberProperty('requiredItemsCount', 0)
