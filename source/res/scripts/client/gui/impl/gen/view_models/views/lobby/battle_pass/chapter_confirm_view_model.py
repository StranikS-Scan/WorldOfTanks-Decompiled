# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/chapter_confirm_view_model.py
from frameworks.wulf import ViewModel

class ChapterConfirmViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ChapterConfirmViewModel, self).__init__(properties=properties, commands=commands)

    def getPrevChapter(self):
        return self._getNumber(0)

    def setPrevChapter(self, value):
        self._setNumber(0, value)

    def getNextChapter(self):
        return self._getNumber(1)

    def setNextChapter(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ChapterConfirmViewModel, self)._initialize()
        self._addNumberProperty('prevChapter', 0)
        self._addNumberProperty('nextChapter', 0)
