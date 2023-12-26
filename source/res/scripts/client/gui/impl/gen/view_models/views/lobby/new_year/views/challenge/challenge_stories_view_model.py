# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/challenge_stories_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ChallengeStoriesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ChallengeStoriesViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectIndex(self):
        return self._getNumber(0)

    def setSelectIndex(self, value):
        self._setNumber(0, value)

    def getAmountOfCompletedStories(self):
        return self._getNumber(1)

    def setAmountOfCompletedStories(self, value):
        self._setNumber(1, value)

    def getStories(self):
        return self._getArray(2)

    def setStories(self, value):
        self._setArray(2, value)

    @staticmethod
    def getStoriesType():
        return unicode

    def _initialize(self):
        super(ChallengeStoriesViewModel, self)._initialize()
        self._addNumberProperty('selectIndex', 0)
        self._addNumberProperty('amountOfCompletedStories', 0)
        self._addArrayProperty('stories', Array())
