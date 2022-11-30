# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/challenge_stories_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ChallengeStoriesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ChallengeStoriesViewModel, self).__init__(properties=properties, commands=commands)

    def getStoryBy(self):
        return self._getString(0)

    def setStoryBy(self, value):
        self._setString(0, value)

    def getSelectIndex(self):
        return self._getNumber(1)

    def setSelectIndex(self, value):
        self._setNumber(1, value)

    def getIsMaxAtmosphereLevel(self):
        return self._getBool(2)

    def setIsMaxAtmosphereLevel(self, value):
        self._setBool(2, value)

    def getStories(self):
        return self._getArray(3)

    def setStories(self, value):
        self._setArray(3, value)

    @staticmethod
    def getStoriesType():
        return str

    def _initialize(self):
        super(ChallengeStoriesViewModel, self)._initialize()
        self._addStringProperty('storyBy', '')
        self._addNumberProperty('selectIndex', 0)
        self._addBoolProperty('isMaxAtmosphereLevel', False)
        self._addArrayProperty('stories', Array())
