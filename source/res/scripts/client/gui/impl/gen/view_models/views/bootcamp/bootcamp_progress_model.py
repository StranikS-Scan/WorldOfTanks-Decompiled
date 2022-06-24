# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/bootcamp_progress_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.bootcamp.bootcamp_lesson_model import BootcampLessonModel

class BootcampProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BootcampProgressModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLesson(self):
        return self._getNumber(0)

    def setCurrentLesson(self, value):
        self._setNumber(0, value)

    def getTotalLessons(self):
        return self._getNumber(1)

    def setTotalLessons(self, value):
        self._setNumber(1, value)

    def getLevels(self):
        return self._getArray(2)

    def setLevels(self, value):
        self._setArray(2, value)

    @staticmethod
    def getLevelsType():
        return BootcampLessonModel

    def _initialize(self):
        super(BootcampProgressModel, self)._initialize()
        self._addNumberProperty('currentLesson', 0)
        self._addNumberProperty('totalLessons', 0)
        self._addArrayProperty('levels', Array())
