# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/chapter_model.py
from frameworks.wulf import ViewModel

class ChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ChapterModel, self).__init__(properties=properties, commands=commands)

    def getChapterId(self):
        return self._getNumber(0)

    def setChapterId(self, value):
        self._setNumber(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(ChapterModel, self)._initialize()
        self._addNumberProperty('chapterId', 0)
        self._addBoolProperty('isCompleted', False)
