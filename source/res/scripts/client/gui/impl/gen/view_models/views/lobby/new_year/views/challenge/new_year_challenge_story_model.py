# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_story_model.py
from frameworks.wulf import ViewModel

class NewYearChallengeStoryModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearChallengeStoryModel, self).__init__(properties=properties, commands=commands)

    def getAvailableStories(self):
        return self._getNumber(0)

    def setAvailableStories(self, value):
        self._setNumber(0, value)

    def getTotalStories(self):
        return self._getNumber(1)

    def setTotalStories(self, value):
        self._setNumber(1, value)

    def getStoryBy(self):
        return self._getString(2)

    def setStoryBy(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearChallengeStoryModel, self)._initialize()
        self._addNumberProperty('availableStories', 0)
        self._addNumberProperty('totalStories', 0)
        self._addStringProperty('storyBy', '')
